# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from hydrogram import Client, filters
from hydrogram.types import ChatPermissions, ChatPrivileges, Message

from config import PREFIXES
from eduu.database.warns import (
    add_warns,
    get_warn_action,
    get_warns,
    get_warns_limit,
    reset_warns,
    set_warn_action,
    set_warns_limit,
)
from eduu.utils import commands, get_target_user
from eduu.utils.consts import ADMIN_STATUSES
from eduu.utils.decorators import require_admin
from eduu.utils.localization import use_chat_lang


def get_warn_reason_text(c: Client, m: Message) -> Message:
    reply = m.reply_to_message
    spilt_text = m.text.split

    if not reply and len(spilt_text()) >= 3:
        return spilt_text(None, 2)[2]
    if reply and len(spilt_text()) >= 2:
        return spilt_text(None, 1)[1]

    return None


@Client.on_message(filters.command("warn", PREFIXES) & filters.group)
@require_admin(ChatPrivileges(can_restrict_members=True))
@use_chat_lang
async def warn_user(c: Client, m: Message, s):
    target_user = await get_target_user(c, m)
    warns_limit = await get_warns_limit(m.chat.id)
    check_admin = await m.chat.get_member(target_user.id)
    reason = get_warn_reason_text(c, m)
    warn_action = await get_warn_action(m.chat.id)

    if check_admin.status in ADMIN_STATUSES:
        await m.reply_text(s("warn_cant_admin"))
        return

    await add_warns(m.chat.id, target_user.id, 1)
    user_warns = await get_warns(m.chat.id, target_user.id)
    if user_warns >= warns_limit:
        if warn_action == "ban":
            await m.chat.ban_member(target_user.id)
            warn_string = s("warn_banned")
        elif warn_action == "mute":
            await m.chat.restrict_member(target_user.id, ChatPermissions(can_send_messages=False))
            warn_string = s("warn_muted")
        elif warn_action == "kick":
            await m.chat.ban_member(target_user.id)
            await m.chat.unban_member(target_user.id)
            warn_string = s("warn_kicked")
        else:
            return

        warn_text = warn_string.format(target_user=target_user.mention, warn_count=user_warns)
        await reset_warns(m.chat.id, target_user.id)
    else:
        warn_text = s("warn_warned").format(
            target_user=target_user.mention,
            warn_count=user_warns,
            warn_limit=warns_limit,
        )
    if reason:
        await m.reply_text(warn_text + "\n" + s("warn_reason_text").format(reason_text=reason))
    else:
        await m.reply_text(warn_text)


@Client.on_message(filters.command("setwarnslimit", PREFIXES) & filters.group)
@require_admin(ChatPrivileges(can_restrict_members=True, can_change_info=True))
@use_chat_lang
async def on_set_warns_limit(c: Client, m: Message, s):
    if len(m.command) == 1:
        await m.reply_text(s("warn_limit_help"))
        return

    try:
        warns_limit = int(m.command[1])
    except ValueError:
        await m.reply_text(s("warn_limit_invalid"))
    else:
        set_warns_limit(m.chat.id, warns_limit)
        await m.reply_text(s("warn_limit_changed").format(warn_limit=warns_limit))


@Client.on_message(filters.command(["resetwarns", "unwarn"], PREFIXES) & filters.group)
@require_admin(ChatPrivileges(can_restrict_members=True))
@use_chat_lang
async def unwarn_user(c: Client, m: Message, s):
    target_user = await get_target_user(c, m)
    await reset_warns(m.chat.id, target_user.id)
    await m.reply_text(s("warn_reset").format(target_user=target_user.mention))


@Client.on_message(filters.command("warns", PREFIXES) & filters.group)
@require_admin()
@use_chat_lang
async def get_user_warns_cmd(c: Client, m: Message, s):
    target_user = await get_target_user(c, m)
    user_warns = await get_warns(m.chat.id, target_user.id)
    await m.reply_text(
        s("warns_count_string").format(target_user=target_user.mention, warns_count=user_warns)
    )


@Client.on_message(filters.command(["setwarnsaction", "warnsaction"], PREFIXES) & filters.group)
@require_admin(ChatPrivileges(can_restrict_members=True))
@use_chat_lang
async def set_warns_action_cmd(c: Client, m: Message, s):
    if len(m.text.split()) == 1:
        warn_act = await get_warn_action(m.chat.id)
        await m.reply_text(s("warn_action_status").format(action=warn_act))
        return

    if m.command[1] not in {"ban", "mute", "kick"}:
        await m.reply_text(s("warns_action_set_invlaid"))
        return

    warn_action_txt = m.command[1]

    await set_warn_action(m.chat.id, warn_action_txt)
    await m.reply_text(s("warns_action_set_string").format(action=warn_action_txt))


commands.add_command("warn", "admin")
commands.add_command("setwarnslimit", "admin")
commands.add_command("resetwarns", "admin")
commands.add_command("warns", "admin")
commands.add_command("setwarnsaction", "admin")
