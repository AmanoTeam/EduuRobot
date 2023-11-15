# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from .core import database

conn = database.get_conn()


async def add_note(chat_id, trigger, raw_data, file_id, note_type):
    await conn.execute(
        "INSERT INTO notes(chat_id, note_name, raw_data, file_id, note_type) VALUES(?, ?, ?, ?, ?)",
        (chat_id, trigger, raw_data, file_id, note_type),
    )
    await conn.commit()


async def update_note(chat_id, trigger, raw_data, file_id, note_type):
    await conn.execute(
        "UPDATE notes SET raw_data = ?, file_id = ?, note_type = ? WHERE chat_id = ? AND note_name = ?",
        (raw_data, file_id, note_type, chat_id, trigger),
    )
    await conn.commit()


async def rm_note(chat_id, trigger):
    await conn.execute("DELETE from notes WHERE chat_id = ? AND note_name = ?", (chat_id, trigger))
    await conn.commit()


async def get_all_notes(chat_id):
    cursor = await conn.execute("SELECT * FROM notes WHERE chat_id = ?", (chat_id,))
    return await cursor.fetchall()
