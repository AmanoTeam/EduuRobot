# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import random

from config import PREFIXES
from pyrogram import Client, filters
from pyrogram.types import Message

from ..utils import commands, http
from ..utils.localization import use_chat_lang


@Client.on_message(filters.command("coub", PREFIXES))
@use_chat_lang()
async def coub(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("coub_usage"))

    text = m.text.split(maxsplit=1)[1]
    r = await http.get("https://coub.com/api/v2/search/coubs", params={"q": text})
    rjson = r.json()
    try:
        content = random.choice(rjson["coubs"])
        links = content["permalink"]
        title = content["title"]
    except IndexError:
        await m.reply_text(strings("no_results", context="general"))
    else:
        await m.reply_text(f'<b><a href="https://coub.com/v/{links}">{title}</a></b>')


commands.add_command("coub", "general")
