# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from typing import Optional

from .core import database

conn = database.get_conn()


async def check_if_del_service(chat_id: int) -> bool:
    cursor = await conn.execute(
        "SELECT delservicemsgs FROM groups WHERE chat_id = ?", (chat_id,)
    )
    row = await cursor.fetchone()
    await cursor.close()
    return row[0]


async def toggle_del_service(chat_id: int, mode: Optional[bool]) -> None:
    await conn.execute(
        "UPDATE groups SET delservicemsgs = ? WHERE chat_id = ?", (mode, chat_id)
    )
    await conn.commit()


async def check_if_antichannelpin(chat_id: int) -> bool:
    cursor = await conn.execute(
        "SELECT antichannelpin FROM groups WHERE chat_id = ?", (chat_id,)
    )
    row = await cursor.fetchone()
    await cursor.close()
    return row[0]


async def toggle_antichannelpin(chat_id: int, mode: Optional[bool]) -> None:
    await conn.execute(
        "UPDATE groups SET antichannelpin = ? WHERE chat_id = ?", (mode, chat_id)
    )
    await conn.commit()
