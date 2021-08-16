# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import TENOR_API_KEY, prefix
from eduu.utils import commands
from eduu.utils.consts import http
from eduu.utils.localization import use_chat_lang
from eduu.utils.bot_error_log import logging_errors

if not TENOR_API_KEY:
    logging.warning(
        f"[{__name__}] You need to fill TENOR_API_KEY in your config file in order to use this plugin."
    )


@Client.on_message(filters.command("gif", prefix))
@use_chat_lang()
@logging_errors
async def gif(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("gif_usage"))

    text = m.text.split(maxsplit=1)[1]
    r = await http.get(
        "https://api.tenor.com/v1/random",
        params=dict(q=text, key=TENOR_API_KEY, limit=1),
    )
    rjson = r.json()
    if rjson["results"]:
        res = rjson["results"][0]["media"][0]["mediumgif"]["url"]
        await m.reply_animation(res)
    else:
        await m.reply_text(strings("no_results", context="general"))


commands.add_command("gif", "general")
