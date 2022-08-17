# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from ..config import PREFIXES
from ..database.warns import (
    add_warns,
    get_warn_action,
    get_warns,
    get_warns_limit,
    reset_warns,
    set_warn_action,
    set_warns_limit,
)
from ..utils import commands, get_target_user
from ..utils.consts import admin_status
from ..utils.decorators import require_admin
from ..utils.localization import use_chat_lang


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


@Client.on_message(filters.command("warn", PREFIXES) & filters.group)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def warn_user(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    warns_limit = await get_warns_limit(m.chat.id)
    check_admin = await m.chat.get_member(target_user.id)
    reason = await get_warn_reason_text(c, m)
    warn_action = await get_warn_action(m.chat.id)
    if check_admin.status not in admin_status:
        await add_warns(m.chat.id, target_user.id, 1)
        user_warns = await get_warns(m.chat.id, target_user.id)
        if user_warns >= warns_limit:
            if warn_action == "ban":
                await m.chat.ban_member(target_user.id)
                warn_string = strings("warn_banned")
            elif warn_action == "mute":
                await m.chat.restrict_member(
                    target_user.id, ChatPermissions(can_send_messages=False)
                )
                warn_string = strings("warn_muted")
            elif warn_action == "kick":
                await m.chat.ban_member(target_user.id)
                await m.chat.unban_member(target_user.id)
                warn_string = strings("warn_kicked")
            else:
                return

            warn_text = warn_string.format(
                target_user=target_user.mention, warn_count=user_warns
            )
            await reset_warns(m.chat.id, target_user.id)
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


@Client.on_message(filters.command("setwarnslimit", PREFIXES) & filters.group)
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


@Client.on_message(filters.command(["resetwarns", "unwarn"], PREFIXES) & filters.group)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def unwarn_user(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    await reset_warns(m.chat.id, target_user.id)
    await m.reply_text(strings("warn_reset").format(target_user=target_user.mention))


@Client.on_message(filters.command("warns", PREFIXES) & filters.group)
@require_admin()
@use_chat_lang()
async def get_user_warns_cmd(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    user_warns = await get_warns(m.chat.id, target_user.id)
    await m.reply_text(
        strings("warns_count_string").format(
            target_user=target_user.mention, warns_count=user_warns
        )
    )


@Client.on_message(
    filters.command(["setwarnsaction", "warnsaction"], PREFIXES) & filters.group
)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def set_warns_action_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        if not m.command[1] in ("ban", "mute", "kick"):
            return await m.reply_text(strings("warns_action_set_invlaid"))

        warn_action_txt = m.command[1]

        await set_warn_action(m.chat.id, warn_action_txt)
        await m.reply_text(
            strings("warns_action_set_string").format(action=warn_action_txt)
        )
    else:
        warn_act = await get_warn_action(m.chat.id)
        await m.reply_text(strings("warn_action_status").format(action=warn_act))


commands.add_command("warn", "admin")
commands.add_command("setwarnslimit", "admin")
commands.add_command("resetwarns", "admin")
commands.add_command("warns", "admin")
commands.add_command("setwarnsaction", "admin")
