# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2018-2021 Amano Team

from pyrogram import Client
from pyrogram.types import Message

from eduu.utils import add_chat, chat_exists

# This is the first plugin run to guarantee
# that the actual chat is initialized in the DB.


@Client.on_message(group=-1)
async def check_chat(c: Client, m: Message):
    chat_id = m.chat.id
    chat_type = m.chat.type

    if not chat_exists(chat_id, chat_type):
        add_chat(chat_id, chat_type)
