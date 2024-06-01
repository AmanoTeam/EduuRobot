# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from hydrogram import Client, filters
from hydrogram.types import ChatPrivileges, Message

from config import PREFIXES
from eduu.utils import commands, extract_time, get_reason_text, get_target_user
from eduu.utils.consts import ADMIN_STATUSES
from eduu.utils.decorators import require_admin
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("ban", PREFIXES))
@use_chat_lang
@require_admin(ChatPrivileges(can_restrict_members=True))
async def ban(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = get_reason_text(c, m)
    check_admin = await m.chat.get_member(target_user.id)
    if check_admin.status in ADMIN_STATUSES:
        await m.reply_text(strings("i_cant_ban_admins"))
        return

    await m.chat.ban_member(target_user.id)
    text = strings("ban_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(text + "\n" + strings("reason_string").format(reason_text=reason))
    else:
        await m.reply_text(text)


@Client.on_message(filters.command("kick", PREFIXES))
@use_chat_lang
@require_admin(ChatPrivileges(can_restrict_members=True))
async def kick(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = get_reason_text(c, m)
    check_admin = await m.chat.get_member(target_user.id)
    if check_admin.status in ADMIN_STATUSES:
        await m.reply_text(strings("i_cant_kick_admins"))
        return

    await m.chat.ban_member(target_user.id)
    await m.chat.unban_member(target_user.id)
    text = strings("kick_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(text + "\n" + strings("reason_string").format(reason_text=reason))
    else:
        await m.reply_text(text)


@Client.on_message(filters.command("unban", PREFIXES))
@use_chat_lang
@require_admin(ChatPrivileges(can_restrict_members=True))
async def unban(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = get_reason_text(c, m)
    await m.chat.unban_member(target_user.id)
    text = strings("unban_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(text + "\n" + strings("reason_string").format(reason_text=reason))
    else:
        await m.reply_text(text)


@Client.on_message(filters.command("tban", PREFIXES))
@use_chat_lang
@require_admin(ChatPrivileges(can_restrict_members=True))
async def tban(c: Client, m: Message, strings):
    if len(m.command) == 1:
        await m.reply_text(strings("error_must_specify_time").format(command=m.command[0]))
        return

    split_time = m.text.split(None, 1)
    ban_time = await extract_time(m, split_time[1])
    if not ban_time:
        return
    await m.chat.ban_member(m.reply_to_message.from_user.id, until_date=ban_time)

    await m.reply_text(
        strings("tban_success").format(
            user=m.reply_to_message.from_user.mention,
            admin=m.from_user.mention,
            time=split_time[1],
        )
    )


commands.add_command("ban", "admin")
commands.add_command("kick", "admin")
commands.add_command("tban", "admin")
commands.add_command("unban", "admin")
