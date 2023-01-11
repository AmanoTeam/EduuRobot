# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from .core import database

conn = database.get_conn()


async def add_filter(chat_id, trigger, raw_data, file_id, filter_type):
    await conn.execute(
        "INSERT INTO filters(chat_id, filter_name, raw_data, file_id, filter_type) VALUES(?, ?, ?, ?, ?)",
        (chat_id, trigger, raw_data, file_id, filter_type),
    )
    await conn.commit()


async def update_filter(chat_id, trigger, raw_data, file_id, filter_type):
    await conn.execute(
        "UPDATE filters SET raw_data = ?, file_id = ?, filter_type = ? WHERE chat_id = ? AND filter_name = ?",
        (raw_data, file_id, filter_type, chat_id, trigger),
    )
    await conn.commit()


async def rm_filter(chat_id, trigger):
    await conn.execute(
        "DELETE from filters WHERE chat_id = ? AND filter_name = ?", (chat_id, trigger)
    )
    await conn.commit()


async def get_all_filters(chat_id):
    cursor = await conn.execute("SELECT * FROM filters WHERE chat_id = ?", (chat_id,))
    return await cursor.fetchall()
