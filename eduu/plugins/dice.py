# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES

from ..utils import commands
from ..utils.localization import use_chat_lang


@Client.on_message(filters.command(["dice", "dados"], PREFIXES))
@use_chat_lang()
async def dice(c: Client, m: Message, strings):
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.id)
    await dicen.reply_text(
        strings("result").format(number=dicen.dice.value), quote=True
    )


commands.add_command("dice", "general")
