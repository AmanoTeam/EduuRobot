# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2018-2021 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message
from telegraph import upload_file

from eduu.config import prefix
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("telegraph", prefix))
@use_chat_lang()
async def telegraph(c: Client, m: Message, strings):
    if m.reply_to_message:
        if (
            m.reply_to_message.photo
            or m.reply_to_message.video
            or m.reply_to_message.animation
        ):
            d_file = await m.reply_to_message.download()
            media_urls = upload_file(d_file)
            tele_link = "https://telegra.ph" + media_urls[0]
            await m.reply_text(tele_link)
    else:
        await m.reply_text(strings("telegraph_err_no_reply"))
