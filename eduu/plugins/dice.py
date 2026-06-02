# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2026 Amano LLC

from __future__ import annotations

from typing import TYPE_CHECKING

from hydrogram import Client, filters

from config import PREFIXES
from eduu.utils import commands
from eduu.utils.localization import Strings, use_chat_lang

if TYPE_CHECKING:
    from hydrogram.types import Message


@Client.on_message(filters.command(["dice", "dados"], PREFIXES))
@use_chat_lang
async def dice(c: Client, m: Message, s: Strings):
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.id)
    await dicen.reply_text(s("dice_result").format(number=dicen.dice.value), quote=True)


commands.add_command("dice", "general")
