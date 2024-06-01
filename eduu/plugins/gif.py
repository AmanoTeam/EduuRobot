# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, TENOR_API_KEY
from eduu.utils import commands, http
from eduu.utils.localization import use_chat_lang

logger = logging.getLogger(__name__)

if not TENOR_API_KEY:
    logger.warning(
        "You need to fill TENOR_API_KEY in your config file in order to use this plugin."
    )


@Client.on_message(filters.command("gif", PREFIXES))
@use_chat_lang
async def gif(c: Client, m: Message, strings):
    if len(m.command) == 1:
        await m.reply_text(strings("gif_usage"))
        return

    text = m.text.split(maxsplit=1)[1]
    r = await http.get(
        "https://api.tenor.com/v1/random",
        params={"q": text, "key": TENOR_API_KEY, "limit": 1},
    )
    rjson = r.json()
    if not rjson["results"]:
        await m.reply_text(strings("no_results", context="general"))
        return

    res = rjson["results"][0]["media"][0]["mediumgif"]["url"]
    await m.reply_animation(res)


commands.add_command("gif", "general")
