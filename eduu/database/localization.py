# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from hydrogram.enums import ChatType

from eduu.utils.consts import GROUP_TYPES

from .core import database

conn = database.get_conn()


async def set_db_lang(chat_id: int, chat_type: str, lang_code: str):
    if chat_type in {ChatType.PRIVATE, ChatType.BOT}:
        await conn.execute(
            "UPDATE users SET chat_lang = ? WHERE user_id = ?", (lang_code, chat_id)
        )
        await conn.commit()
    elif chat_type in GROUP_TYPES:  # groups and supergroups share the same table
        await conn.execute(
            "UPDATE groups SET chat_lang = ? WHERE chat_id = ?", (lang_code, chat_id)
        )
        await conn.commit()
    elif chat_type == ChatType.CHANNEL:
        await conn.execute(
            "UPDATE channels SET chat_lang = ? WHERE chat_id = ?", (lang_code, chat_id)
        )
        await conn.commit()
    else:
        raise TypeError(f"Unknown chat type '{chat_type}'.")


async def get_db_lang(chat_id: int, chat_type: str) -> str:
    if chat_type == ChatType.PRIVATE:
        cursor = await conn.execute("SELECT chat_lang FROM users WHERE user_id = ?", (chat_id,))
        ul = await cursor.fetchone()
    elif chat_type in GROUP_TYPES:  # groups and supergroups share the same table
        cursor = await conn.execute("SELECT chat_lang FROM groups WHERE chat_id = ?", (chat_id,))
        ul = await cursor.fetchone()
    elif chat_type == ChatType.CHANNEL:
        cursor = await conn.execute("SELECT chat_lang FROM channels WHERE chat_id = ?", (chat_id,))
        ul = await cursor.fetchone()
    else:
        raise TypeError(f"Unknown chat type '{chat_type}'.")
    return ul[0] if ul else None
