# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from eduu.utils import http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("telegraph", PREFIXES))
@use_chat_lang
async def telegraph(c: Client, m: Message, strings):
    if not m.reply_to_message:
        return await m.reply_text(strings("telegraph_err_no_reply"))

    if not (m.reply_to_message.photo or m.reply_to_message.video or m.reply_to_message.animation):
        return None

    d_file = await m.reply_to_message.download()
    with Path(d_file).open("rb") as f:
        response = await http.post("https://telegra.ph/upload", files={"upload-file": f})
    tele_link = "https://telegra.ph" + response.json()[0]["src"]
    await m.reply_text(tele_link)
    return None
