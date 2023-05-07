# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import asyncio

from config import PREFIXES
from pyrogram import Client, filters
from pyrogram.types import Message

from ...database.admins import check_if_del_service, toggle_del_service
from ...utils import commands
from ...utils.decorators import require_admin
from ...utils.localization import use_chat_lang


@Client.on_message(filters.command("purge", PREFIXES))
@require_admin(permissions=["can_delete_messages"], allow_in_private=True)
@use_chat_lang()
async def purge(c: Client, m: Message, strings):
    """Purge upto the replied message."""
    status_message = await m.reply_text(strings("purge_in_progress"), quote=True)
    await m.delete()
    message_ids = []
    count_del_etion_s = 0
    if m.reply_to_message:
        for a_s_message_id in range(m.reply_to_message.id, m.id):
            message_ids.append(a_s_message_id)
            if len(message_ids) == 100:
                await c.delete_messages(chat_id=m.chat.id, message_ids=message_ids)
                count_del_etion_s += len(message_ids)
                message_ids = []
        if len(message_ids) > 0:
            await c.delete_messages(chat_id=m.chat.id, message_ids=message_ids)
            count_del_etion_s += len(message_ids)
    await status_message.edit_text(
        strings("purge_success").format(count=count_del_etion_s),
    )
    await asyncio.sleep(5)
    await status_message.delete()


@Client.on_message(filters.command("cleanservice", PREFIXES))
@require_admin(permissions=["can_delete_messages"])
@use_chat_lang()
async def delservice(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        if m.command[1] == "on":
            await toggle_del_service(m.chat.id, True)
            await m.reply_text(strings("cleanservice_enabled"))
        elif m.command[1] == "off":
            await toggle_del_service(m.chat.id, None)
            await m.reply_text(strings("cleanservice_disabled"))
        else:
            await m.reply_text(strings("cleanservice_invalid_arg"))
    else:
        check_delservice = await check_if_del_service(m.chat.id)
        if check_delservice is None:
            await m.reply_text(strings("cleanservice_status_disabled"))
        else:
            await m.reply_text(strings("cleanservice_status_enabled"))


@Client.on_message(filters.service, group=-1)
async def delservice_action(c: Client, m: Message):
    get_delservice = await check_if_del_service(m.chat.id)
    if not get_delservice:
        return

    self_member = await m.chat.get_member("me")

    if self_member.privileges and self_member.privileges.can_delete_messages:
        await m.delete()


commands.add_command("cleanservice", "admin")
commands.add_command("purge", "admin")
