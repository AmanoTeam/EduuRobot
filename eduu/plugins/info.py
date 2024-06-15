# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import html
from contextlib import suppress

from hydrogram import Client, filters
from hydrogram.enums import ChatMemberStatus
from hydrogram.errors import BadRequest, UserNotParticipant
from hydrogram.types import Message

from config import PREFIXES
from eduu.utils import commands
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("info", PREFIXES))
@use_chat_lang
async def user_info(c: Client, m: Message, s):
    if len(m.command) == 2:
        try:
            user = await c.get_users(
                int(m.command[1]) if m.command[1].isdecimal() else m.command[1]
            )
        except BadRequest:
            await m.reply_text(s("info_user_not_found").format(user=m.command[1]))
            return

    elif m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user

    text = s("info_header")
    text += s("info_id").format(id=user.id)
    text += s("info_first_name").format(first_name=html.escape(user.first_name))

    if user.last_name:
        text += s("info_last_name").format(last_name=html.escape(user.last_name))

    if user.username:
        text += s("info_username").format(username=html.escape(user.username))

    text += s("info_userlink").format(link=user.mention("link", style="html"))

    with suppress((UserNotParticipant, ValueError)):
        member = await m.chat.get_member(user.id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            text += s("info_chat_admin")
        elif member.status == ChatMemberStatus.OWNER:
            text += s("info_chat_owner")

    await m.reply_text(text)


commands.add_command("info", "tools")
