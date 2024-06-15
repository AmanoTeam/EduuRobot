# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import html

from hydrogram import Client, filters
from hydrogram.errors.exceptions import BadRequest
from hydrogram.types import Message

from config import PREFIXES
from eduu.utils import commands
from eduu.utils.localization import Strings, use_chat_lang


@Client.on_message(filters.command("id", PREFIXES) & filters.private)
@use_chat_lang
async def ids_private(c: Client, m: Message, s: Strings):
    if len(m.command) == 2:
        try:
            user_data = await c.get_users(
                int(m.command[1]) if m.command[1].isdecimal() else m.command[1]
            )
        except BadRequest:
            await m.reply_text(s("id_user_not_found").format(user=m.command[1]))
            return
    else:
        user_data = m.from_user

    await m.reply_text(
        s("id_info_private").format(
            first_name=user_data.first_name,
            last_name=user_data.last_name or "",
            username=f"@{user_data.username}" if user_data.username else s("id_none"),
            user_id=user_data.id,
            user_dc=user_data.dc_id or s("id_unknown"),
            lang=user_data.language_code or s("id_unknown"),
            chat_type=m.chat.type,
        )
    )


@Client.on_message(filters.command("id", PREFIXES) & filters.group)
@use_chat_lang
async def ids(c: Client, m: Message, s: Strings):
    if len(m.command) == 2:
        try:
            user_data = await c.get_users(
                int(m.command[1]) if m.command[1].isdecimal() else m.command[1]
            )
        except BadRequest:
            await m.reply_text(s("id_user_not_found").format(user=m.command[1]))
            return

    elif m.reply_to_message:
        user_data = m.reply_to_message.from_user
    else:
        user_data = m.from_user

    await m.reply_text(
        s("id_info_group").format(
            first_name=html.escape(user_data.first_name),
            last_name=html.escape(user_data.last_name or ""),
            username=f"@{user_data.username}" if user_data.username else s("id_none"),
            user_id=user_data.id,
            user_dc=user_data.dc_id or s("id_unknown"),
            lang=user_data.language_code or s("id_unknown"),
            chat_title=m.chat.title,
            chat_username=f"@{m.chat.username}" if m.chat.username else s("id_none"),
            chat_id=m.chat.id,
            chat_dc=m.chat.dc_id or s("id_unknown"),
            chat_type=m.chat.type,
            message_id=m.id + 1,
        )
    )


commands.add_command("id", "tools")
