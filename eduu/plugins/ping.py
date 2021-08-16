# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands
from eduu.utils.bot_error_log import logging_errors


@Client.on_message(filters.command("ping", prefix))
@logging_errors
async def ping(c: Client, m: Message):
    first = datetime.now()
    sent = await m.reply_text("<b>Pong!</b>")
    second = datetime.now()
    await sent.edit_text(
        f"<b>Pong!</b> <code>{(second - first).microseconds / 1000}</code>ms"
    )


commands.add_command("ping", "general")
