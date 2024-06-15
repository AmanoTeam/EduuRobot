# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from hydrogram import Client, filters
from hydrogram.types import ChatPermissions, ChatPrivileges, Message

from config import PREFIXES
from eduu.utils import commands, extract_time, get_reason_text, get_target_user
from eduu.utils.consts import ADMIN_STATUSES
from eduu.utils.decorators import require_admin
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("mute", PREFIXES))
@use_chat_lang
@require_admin(ChatPrivileges(can_restrict_members=True))
async def mute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = get_reason_text(c, m)
    check_admin = await m.chat.get_member(target_user.id)
    if check_admin.status in ADMIN_STATUSES:
        await m.reply_text(strings("mute_cannot_mute_admins"))
        return

    await m.chat.restrict_member(target_user.id, ChatPermissions(can_send_messages=False))
    text = strings("mute_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(
            text + "\n" + strings("admins_reason_string").format(reason_text=reason)
        )
    else:
        await m.reply_text(text)


@Client.on_message(filters.command("unmute", PREFIXES))
@use_chat_lang
@require_admin(ChatPrivileges(can_restrict_members=True))
async def unmute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = get_reason_text(c, m)
    await m.chat.unban_member(target_user.id)
    text = strings("unmute_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(
            text + "\n" + strings("admins_reason_string").format(reason_text=reason)
        )
    else:
        await m.reply_text(text)


@Client.on_message(filters.command("tmute", PREFIXES))
@use_chat_lang
@require_admin(ChatPrivileges(can_restrict_members=True))
async def tmute(c: Client, m: Message, strings):
    if len(m.command) == 1:
        await m.reply_text(strings("admins_error_must_specify_time").format(command=m.command[0]))
        return

    split_time = m.text.split(None, 1)
    mute_time = await extract_time(m, split_time[1])
    if not mute_time:
        return
    await m.chat.restrict_member(
        m.reply_to_message.from_user.id,
        ChatPermissions(can_send_messages=False),
        until_date=mute_time,
    )
    await m.reply_text(
        strings("tmute_success").format(
            user=m.reply_to_message.from_user.mention,
            admin=m.from_user.mention,
            time=split_time[1],
        )
    )


commands.add_command("mute", "admin")
commands.add_command("tmute", "admin")
commands.add_command("unmute", "admin")
