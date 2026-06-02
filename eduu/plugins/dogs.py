# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2026 Amano LLC

from __future__ import annotations

from typing import TYPE_CHECKING

from hydrogram import Client, filters

from config import PREFIXES
from eduu.utils import commands, http
from eduu.utils.localization import Strings, use_chat_lang

if TYPE_CHECKING:
    from hydrogram.types import Message


@Client.on_message(filters.command("dog", PREFIXES))
@use_chat_lang
async def dog(c: Client, m: Message, s: Strings):
    r = await http.get("https://random.dog/woof.json")
    rj = r.json()

    await m.reply_photo(rj["url"], caption=s("dog_woof"))


commands.add_command("dog", "general")
