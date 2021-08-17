# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2018-2021 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands
from eduu.utils.consts import http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("cat", prefix))
@use_chat_lang()
async def cat(c: Client, m: Message, strings):
    r = await http.get("https://api.thecatapi.com/v1/images/search")
    rj = r.json()

    await m.reply_photo(rj[0]["url"], caption=strings("meow"))


commands.add_command("cat", "general")
