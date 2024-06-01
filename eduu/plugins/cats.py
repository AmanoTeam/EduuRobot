# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from eduu.utils import commands, http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("cat", PREFIXES))
@use_chat_lang
async def cat(c: Client, m: Message, strings):
    r = await http.get("https://api.thecatapi.com/v1/images/search")
    rj = r.json()

    if rj[0]["url"].endswith(".gif"):
        await m.reply_animation(rj[0]["url"], caption=strings("meow"))
    else:
        await m.reply_photo(rj[0]["url"], caption=strings("meow"))


commands.add_command("cat", "general")
