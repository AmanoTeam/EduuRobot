# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from pyrogram import Client
from pyrogram.types import Message

from ..database.chats import add_chat, chat_exists

# This is the first plugin run to guarantee
# that the actual chat is initialized in the DB.


@Client.on_message(group=-1)
async def check_chat(c: Client, m: Message):
    chat_id = m.chat.id
    chat_type = m.chat.type
    chatexists = await chat_exists(chat_id, chat_type)

    if not chatexists:
        await add_chat(chat_id, chat_type)
