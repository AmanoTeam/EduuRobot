# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import html
from contextlib import suppress

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import BadRequest, UserNotParticipant
from pyrogram.types import Message

from config import PREFIXES
from eduu.utils import commands
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("info", PREFIXES))
@use_chat_lang
async def user_info(c: Client, m: Message, strings):
    if len(m.command) == 2:
        try:
            user = await c.get_users(
                int(m.command[1]) if m.command[1].isdecimal() else m.command[1]
            )
        except BadRequest:
            return await m.reply_text(
                strings("user_not_found").format(user=m.command[1])
            )
    elif m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user

    text = strings("info_header")
    text += strings("info_id").format(id=user.id)
    text += strings("info_first_name").format(first_name=html.escape(user.first_name))

    if user.last_name:
        text += strings("info_last_name").format(last_name=html.escape(user.last_name))

    if user.username:
        text += strings("info_username").format(username=html.escape(user.username))

    text += strings("info_userlink").format(link=user.mention("link", style="html"))

    with suppress((UserNotParticipant, ValueError)):
        member = await m.chat.get_member(user.id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            text += strings("info_chat_admin")
        elif member.status == ChatMemberStatus.OWNER:
            text += strings("info_chat_owner")

    await m.reply_text(text)
    return None


commands.add_command("info", "tools")
