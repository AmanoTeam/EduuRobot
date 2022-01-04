# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import asyncio
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.database import db, dbc
from eduu.utils import commands, require_admin
from eduu.utils.localization import use_chat_lang


def check_if_del_service(chat_id):
    dbc.execute("SELECT delservicemsgs FROM groups WHERE chat_id = ?", (chat_id,))
    res = dbc.fetchone()[0]
    return res


def toggle_del_service(chat_id: int, mode: Optional[bool]):
    dbc.execute(
        "UPDATE groups SET delservicemsgs = ? WHERE chat_id = ?", (mode, chat_id)
    )
    db.commit()


@Client.on_message(filters.command("purge", prefix))
@require_admin(permissions=["can_delete_messages"], allow_in_private=True)
@use_chat_lang(context="admin")
async def purge(c: Client, m: Message, strings):
    """Purge upto the replied message."""
    status_message = await m.reply_text(strings("purge_in_progress"), quote=True)
    await m.delete()
    message_ids = []
    count_del_etion_s = 0
    if m.reply_to_message:
        for a_s_message_id in range(m.reply_to_message.message_id, m.message_id):
            message_ids.append(a_s_message_id)
            if len(message_ids) == 100:
                await c.delete_messages(chat_id=m.chat.id, message_ids=message_ids)
                count_del_etion_s += len(message_ids)
                message_ids = []
        if len(message_ids) > 0:
            await c.delete_messages(chat_id=m.chat.id, message_ids=message_ids)
            count_del_etion_s += len(message_ids)
    await status_message.edit_text(
        strings("purge_success").format(count=count_del_etion_s)
    )
    await asyncio.sleep(5)
    await status_message.delete()


@Client.on_message(filters.command("cleanservice", prefix))
@require_admin(permissions=["can_delete_messages"])
@use_chat_lang(context="admin")
async def delservice(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        if m.command[1] == "on":
            toggle_del_service(m.chat.id, True)
            await m.reply_text(strings("cleanservice_enabled"))
        elif m.command[1] == "off":
            toggle_del_service(m.chat.id, None)
            await m.reply_text(strings("cleanservice_disabled"))
        else:
            await m.reply_text(strings("cleanservice_invalid_arg"))
    else:
        check_delservice = check_if_del_service(m.chat.id)
        if check_delservice is None:
            await m.reply_text(strings("cleanservice_status_disabled"))
        elif check_delservice is not None:
            await m.reply_text(strings("cleanservice_status_enabled"))


@Client.on_message(filters.service, group=-1)
async def delservice_action(c: Client, m: Message):
    get_delservice = check_if_del_service(m.chat.id)
    getmychatmember = await m.chat.get_member("me")
    if (get_delservice and getmychatmember.can_delete_messages) is True:
        await m.delete()
    else:
        pass


commands.add_command("cleanservice", "admin")
commands.add_command("purge", "admin")
