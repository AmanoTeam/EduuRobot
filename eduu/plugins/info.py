# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import html

from pyrogram import Client, filters
from pyrogram.errors import BadRequest, UserNotParticipant
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands
from eduu.utils.localization import use_chat_lang
from eduu.utils.bot_error_log import logging_errors


@Client.on_message(filters.command("info", prefix))
@use_chat_lang()
@logging_errors
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

    try:
        member = await c.get_chat_member(chat_id=m.chat.id, user_id=user.id)
        if member.status in ["administrator"]:
            text += strings("info_chat_admin")
        elif member.status in ["creator"]:
            text += strings("info_chat_creator")
    except (UserNotParticipant, ValueError):
        pass

    await m.reply_text(text)


commands.add_command("info", "tools")
