# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from typing import Optional

from .core import database

conn = database.get_conn()


async def get_warn_action(chat_id: int) -> tuple[Optional[str], bool]:
    cursor = await conn.execute("SELECT warn_action FROM groups WHERE chat_id = (?)", (chat_id,))
    res = (await cursor.fetchone())[0]
    return "ban" if res is None else res


async def set_warn_action(chat_id: int, action: Optional[str]):
    await conn.execute("UPDATE groups SET warn_action = ? WHERE chat_id = ?", (action, chat_id))
    await conn.commit()


async def get_warns(chat_id, user_id):
    cursor = await conn.execute(
        "SELECT count FROM user_warns WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    r = await cursor.fetchone()
    return r[0] if r else 0


async def add_warns(chat_id, user_id, number):
    await conn.execute(
        "SELECT * FROM user_warns WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
    )
    row = await conn.fetchone()
    if row:
        await conn.execute(
            "UPDATE user_warns SET count = count + ? WHERE chat_id = ? AND user_id = ?",
            (number, chat_id, user_id),
        )
    else:
        await conn.execute(
            "INSERT INTO user_warns (user_id, chat_id, count) VALUES (?,?,?)",
            (user_id, chat_id, number),
        )

    await conn.commit()


async def reset_warns(chat_id, user_id):
    await conn.execute(
        "DELETE FROM user_warns WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
    )
    await conn.commit()


async def get_warns_limit(chat_id):
    cursor = await conn.execute("SELECT warns_limit FROM groups WHERE chat_id = ?", (chat_id,))
    res = (await cursor.fetchone())[0]
    return 3 if res is None else res


async def set_warns_limit(chat_id, warns_limit):
    await conn.execute(
        "UPDATE groups SET warns_limit = ? WHERE chat_id = ?", (warns_limit, chat_id)
    )
    await conn.commit()
