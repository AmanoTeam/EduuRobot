# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from __future__ import annotations

from .core import database

conn = database.get_conn()


async def get_welcome(chat_id: int) -> tuple[str | None, bool]:
    cursor = await conn.execute(
        "SELECT welcome, welcome_enabled FROM groups WHERE chat_id = (?)", (chat_id,)
    )
    return await cursor.fetchone()


async def set_welcome(chat_id: int, welcome: str | None):
    await conn.execute("UPDATE groups SET welcome = ? WHERE chat_id = ?", (welcome, chat_id))
    await conn.commit()


async def toggle_welcome(chat_id: int, mode: bool):
    await conn.execute("UPDATE groups SET welcome_enabled = ? WHERE chat_id = ?", (mode, chat_id))
    await conn.commit()
