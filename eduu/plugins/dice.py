# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from hydrogram import Client, filters
from hydrogram.types import Message

from config import PREFIXES
from eduu.utils import commands
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command(["dice", "dados"], PREFIXES))
@use_chat_lang
async def dice(c: Client, m: Message, strings):
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.id)
    await dicen.reply_text(strings("dice_result").format(number=dicen.dice.value), quote=True)


commands.add_command("dice", "general")
