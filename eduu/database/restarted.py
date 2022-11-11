# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from typing import Tuple

from .core import database

conn = database.get_conn()


async def del_restarted():
    await conn.execute("DELETE FROM was_restarted_at")
    await conn.commit()


async def get_restarted() -> Tuple[int, int]:
    cursor = await conn.execute("SELECT chat_id, message_id FROM was_restarted_at")
    return await cursor.fetchone()


async def set_restarted(chat_id: int, message_id: int):
    await conn.execute(
        "INSERT INTO was_restarted_at VALUES (?, ?)", (chat_id, message_id)
    )
    await conn.commit()
