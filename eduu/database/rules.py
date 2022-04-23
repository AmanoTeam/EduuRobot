# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from .core import database

conn = database.get_conn()


async def get_rules(chat_id):
    cursor = await conn.execute(
        "SELECT rules FROM groups WHERE chat_id = (?)", (chat_id,)
    )
    try:
        row = await cursor.fetchone()[0]
        return row
    except IndexError:
        return None


async def set_rules(chat_id, rules):
    await conn.execute(
        "UPDATE groups SET rules = ? WHERE chat_id = ?", (rules, chat_id)
    )
    await conn.commit()
