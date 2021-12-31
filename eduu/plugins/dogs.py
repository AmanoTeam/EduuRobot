# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands, http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("dog", prefix))
@use_chat_lang()
async def dog(c: Client, m: Message, strings):
    r = await http.get("https://random.dog/woof.json")
    rj = r.json()

    await m.reply_photo(rj["url"], caption=strings("woof"))


commands.add_command("dog", "general")
