# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from typing import TYPE_CHECKING

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from eduu.utils import commands, http
from eduu.utils.localization import use_chat_lang

if TYPE_CHECKING:
    from io import BytesIO


@Client.on_message(filters.command("paste", PREFIXES))
@use_chat_lang
async def paste(c: Client, m: Message, strings):
    if not m.reply_to_message:
        return await m.reply_text(strings("reply_to_document_or_text"))

    if m.reply_to_message.document:
        tfile = m.reply_to_message
        out_file: BytesIO = await tfile.download(in_memory=True)
        out_file.read().decode("UTF-8")
    if m.reply_to_message.text:
        mean = m.reply_to_message.text

    url = "https://nekobin.com/api/documents"
    r = await http.post(url, json={"content": mean})
    url = f"https://nekobin.com/{r.json()['result']['key']}"
    await m.reply_text(url, disable_web_page_preview=True)
    return None


commands.add_command("paste", "tools")
