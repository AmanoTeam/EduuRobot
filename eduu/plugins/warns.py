# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

from typing import Optional, Tuple

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from eduu.config import prefix
from eduu.database import db, dbc
from eduu.utils import commands, require_admin
from eduu.utils.consts import admin_status
from eduu.utils.localization import use_chat_lang

from .admin import get_target_user

dbc.execute(
    """
CREATE TABLE IF NOT EXISTS user_warns(
    user_id INTEGER,
    chat_id INTEGER,
    count INTEGER
)
    """
)


async def get_warn_reason_text(c: Client, m: Message) -> Message:
    reply = m.reply_to_message
    spilt_text = m.text.split
    if not reply and len(spilt_text()) >= 3:
        warn_reason = spilt_text(None, 2)[2]
    elif reply and len(spilt_text()) >= 2:
        warn_reason = spilt_text(None, 1)[1]
    else:
        warn_reason = None
    return warn_reason


def get_warn_action(chat_id: int) -> Tuple[Optional[str], bool]:
    dbc.execute("SELECT warn_action FROM groups WHERE chat_id = (?)", (chat_id,))
    res = dbc.fetchone()[0]
    return "ban" if res is None else res


def set_warn_action(chat_id: int, action: Optional[str]):
    dbc.execute(
        "UPDATE groups SET warn_action = ? WHERE chat_id = ?", (action, chat_id)
    )
    db.commit()


def get_warns(chat_id, user_id):
    dbc.execute(
        "SELECT count FROM user_warns WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    r = dbc.fetchone()
    return r[0] if r else 0


def add_warns(chat_id, user_id, number):
    dbc.execute(
        "SELECT * FROM user_warns WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
    )
    if dbc.fetchone():
        dbc.execute(
            "UPDATE user_warns SET count = count + ? WHERE chat_id = ? AND user_id = ?",
            (number, chat_id, user_id),
        )
        db.commit()
    else:
        dbc.execute(
            "INSERT INTO user_warns (user_id, chat_id, count) VALUES (?,?,?)",
            (user_id, chat_id, number),
        )
        db.commit()


def reset_warns(chat_id, user_id):
    dbc.execute(
        "DELETE FROM user_warns WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
    )
    db.commit()


def get_warns_limit(chat_id):
    dbc.execute("SELECT warns_limit FROM groups WHERE chat_id = ?", (chat_id,))
    res = dbc.fetchone()[0]
    return 3 if res is None else res


def set_warns_limit(chat_id, warns_limit):
    dbc.execute(
        "UPDATE groups SET warns_limit = ? WHERE chat_id = ?", (warns_limit, chat_id)
    )
    db.commit()


@Client.on_message(filters.command("warn", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def warn_user(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    warns_limit = get_warns_limit(m.chat.id)
    check_admin = await c.get_chat_member(m.chat.id, target_user.id)
    reason = await get_warn_reason_text(c, m)
    warn_action = get_warn_action(m.chat.id)
    if check_admin.status not in admin_status:
        add_warns(m.chat.id, target_user.id, 1)
        user_warns = get_warns(m.chat.id, target_user.id)
        if user_warns >= warns_limit:
            if warn_action == "ban":
                await c.kick_chat_member(m.chat.id, target_user.id)
                warn_string = strings("warn_banned")
            elif warn_action == "mute":
                await c.restrict_chat_member(
                    m.chat.id, target_user.id, ChatPermissions(can_send_messages=False)
                )
                warn_string = strings("warn_muted")
            elif warn_action == "kick":
                await c.kick_chat_member(m.chat.id, target_user.id)
                await c.unban_chat_member(m.chat.id, target_user.id)
                warn_string = strings("warn_kicked")
            else:
                return

            warn_text = warn_string.format(
                target_user=target_user.mention, warn_count=user_warns
            )
            reset_warns(m.chat.id, target_user.id)
        else:
            warn_text = strings("user_warned").format(
                target_user=target_user.mention,
                warn_count=user_warns,
                warn_limit=warns_limit,
            )
        if reason:
            await m.reply_text(
                warn_text
                + "\n"
                + strings("warn_reason_text").format(reason_text=reason)
            )
        else:
            await m.reply_text(warn_text)
    else:
        await m.reply_text(strings("warn_cant_admin"))


@Client.on_message(filters.command("setwarnslimit", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members", "can_change_info"])
@use_chat_lang()
async def on_set_warns_limit(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("warn_limit_help"))
    try:
        warns_limit = int(m.command[1])
    except ValueError:
        await m.reply_text(strings("warn_limit_invalid"))
    else:
        set_warns_limit(m.chat.id, warns_limit)
        await m.reply(strings("warn_limit_changed").format(warn_limit=warns_limit))


@Client.on_message(filters.command(["resetwarns", "unwarn"], prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def unwarn_user(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reset_warns(m.chat.id, target_user.id)
    await m.reply_text(strings("warn_reset").format(target_user=target_user.mention))


@Client.on_message(filters.command("warns", prefix) & filters.group)
@require_admin()
@use_chat_lang()
async def get_user_warns_cmd(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    user_warns = get_warns(m.chat.id, target_user.id)
    await m.reply_text(
        strings("warns_count_string").format(
            target_user=target_user.mention, warns_count=user_warns
        )
    )


@Client.on_message(
    filters.command(["setwarnsaction", "warnsaction"], prefix) & filters.group
)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def set_warns_action_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        if not m.command[1] in ("ban", "mute", "kick"):
            return await m.reply_text(strings("warns_action_set_invlaid"))

        warn_action_txt = m.command[1]

        set_warn_action(m.chat.id, warn_action_txt)
        await m.reply_text(
            strings("warns_action_set_string").format(action=warn_action_txt)
        )
    else:
        await m.reply_text(
            strings("warn_action_status").format(action=get_warn_action(m.chat.id))
        )


commands.add_command("warn", "admin")
commands.add_command("setwarnslimit", "admin")
commands.add_command("resetwarns", "admin")
commands.add_command("warns", "admin")
commands.add_command("setwarnsaction", "admin")
