# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

from io import BytesIO

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands
from eduu.utils.consts import http
from eduu.utils.localization import use_chat_lang
from eduu.utils.bot_error_log import logging_errors


@Client.on_message(filters.command("print", prefix))
@use_chat_lang()
@logging_errors
async def prints(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("print_usage"), reply_to_message_id=m.message_id
        )
    sent = await m.reply_text(strings("taking_screenshot"))
    text = m.text.split(maxsplit=1)[1]
    r = await http.get("https://webshot.amanoteam.com/print", params=dict(q=text))
    bio = BytesIO(r.read())
    bio.name = "screenshot.png"
    await m.reply_photo(bio)
    await sent.delete()


commands.add_command("print", "tools")
