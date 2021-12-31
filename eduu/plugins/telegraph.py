# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import atexit

from aiograph import Telegraph
from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import run_async
from eduu.utils.localization import use_chat_lang

tgraph = Telegraph()


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
            media_urls = await tgraph.upload(d_file)
            tele_link = "https://telegra.ph" + media_urls[0]
            await m.reply_text(tele_link)
    else:
        await m.reply_text(strings("telegraph_err_no_reply"))


atexit.register(run_async, tgraph.close)
