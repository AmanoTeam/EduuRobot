# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from pathlib import Path

from hydrogram import Client, filters
from hydrogram.types import Message

from config import PREFIXES
from eduu.utils import http
from eduu.utils.localization import Strings, use_chat_lang


@Client.on_message(filters.command("telegraph", PREFIXES))
@use_chat_lang
async def telegraph(c: Client, m: Message, s: Strings):
    if not m.reply_to_message:
        await m.reply_text(s("telegraph_err_no_reply"))
        return

    if not (m.reply_to_message.photo or m.reply_to_message.video or m.reply_to_message.animation):
        return

    d_file = await m.reply_to_message.download()
    with Path(d_file).open("rb") as f:
        response = await http.post("https://telegra.ph/upload", files={"upload-file": f})
    tele_link = "https://telegra.ph" + response.json()[0]["src"]
    await m.reply_text(tele_link)
