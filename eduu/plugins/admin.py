# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import asyncio
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message, User

from eduu.config import prefix
from eduu.database import groups
from eduu.utils import commands, require_admin, time_extract
from eduu.utils.consts import admin_status
from eduu.utils.localization import use_chat_lang


async def get_reason_text(c: Client, m: Message) -> Message:
    reply = m.reply_to_message
    spilt_text = m.text.split
    if not reply and len(spilt_text()) >= 3:
        reason = spilt_text(None, 2)[2]
    elif reply and len(spilt_text()) >= 2:
        reason = spilt_text(None, 1)[1]
    else:
        reason = None
    return reason


async def check_if_antichannelpin(chat_id: int):
    return (await groups.get(chat_id=chat_id)).antichannelpin


async def toggle_antichannelpin(chat_id: int, mode: Optional[bool]):
    await groups.filter(chat_id=chat_id).update(antichannelpin=mode)


async def check_if_del_service(chat_id: int):
    return (await groups.get(chat_id=chat_id)).delservicemsgs


async def toggle_del_service(chat_id: int, mode: Optional[bool]):
    await groups.filter(chat_id=chat_id).update(delservicemsgs=mode)


async def get_target_user(c: Client, m: Message) -> User:
    if m.reply_to_message:
        target_user = m.reply_to_message.from_user
    else:
        msg_entities = m.entities[1] if m.text.startswith("/") else m.entities[0]
        target_user = await c.get_users(
            msg_entities.user.id
            if msg_entities.type == "text_mention"
            else int(m.command[1])
            if m.command[1].isdecimal()
            else m.command[1]
        )
    return target_user


@Client.on_message(filters.command("pin", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def pin(c: Client, m: Message):
    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id,
        disable_notification=True,
        both_sides=True,
    )


@Client.on_message(filters.command("pin loud", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def pinloud(c: Client, m: Message):
    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id,
        disable_notification=False,
        both_sides=True,
    )


@Client.on_message(filters.command("unpin", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def unpin(c: Client, m: Message):
    await c.unpin_chat_message(m.chat.id, m.reply_to_message.message_id)


@Client.on_message(filters.command(["unpinall", "unpin all"], prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def unpinall(c: Client, m: Message):
    await c.unpin_all_chat_messages(m.chat.id)


@Client.on_message(filters.command("ban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def ban(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = await get_reason_text(c, m)
    check_admin = await c.get_chat_member(m.chat.id, target_user.id)
    if check_admin.status not in admin_status:
        await c.kick_chat_member(m.chat.id, target_user.id)
        text = strings("ban_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
        if reason:
            await m.reply_text(
                text + "\n" + strings("reason_string").format(reason_text=reason)
            )
        else:
            await m.reply_text(text)
    else:
        await m.reply_text(strings("i_cant_ban_admins"))


@Client.on_message(filters.command("kick", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def kick(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = await get_reason_text(c, m)
    check_admin = await c.get_chat_member(m.chat.id, target_user.id)
    if check_admin.status not in admin_status:
        await c.kick_chat_member(m.chat.id, target_user.id)
        await m.chat.unban_member(target_user.id)
        text = strings("kick_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
        if reason:
            await m.reply_text(
                text + "\n" + strings("reason_string").format(reason_text=reason)
            )
        else:
            await m.reply_text(text)
    else:
        await m.reply_text(strings("i_cant_kick_admins"))


@Client.on_message(filters.command("unban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def unban(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = await get_reason_text(c, m)
    await m.chat.unban_member(target_user.id)
    text = strings("unban_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(
            text + "\n" + strings("reason_string").format(reason_text=reason)
        )
    else:
        await m.reply_text(text)


@Client.on_message(filters.command("mute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def mute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = await get_reason_text(c, m)
    check_admin = await c.get_chat_member(m.chat.id, target_user.id)
    if check_admin.status not in admin_status:
        await c.restrict_chat_member(
            m.chat.id, target_user.id, ChatPermissions(can_send_messages=False)
        )
        text = strings("mute_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
        if reason:
            await m.reply_text(
                text + "\n" + strings("reason_string").format(reason_text=reason)
            )
        else:
            await m.reply_text(text)
    else:
        await m.reply_text(strings("i_cant_mute_admins"))


@Client.on_message(filters.command("unmute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def unmute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = await get_reason_text(c, m)
    await m.chat.unban_member(target_user.id)
    text = strings("unmute_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(
            text + "\n" + strings("reason_string").format(reason_text=reason)
        )
    else:
        await m.reply_text(text)


@Client.on_message(filters.command("tmute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def tmute(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("error_must_specify_time").format(command=m.command[0])
        )
    split_time = m.text.split(None, 1)
    mute_time = await time_extract(m, split_time[1])
    if not mute_time:
        return
    await c.restrict_chat_member(
        m.chat.id,
        m.reply_to_message.from_user.id,
        ChatPermissions(can_send_messages=False),
        until_date=mute_time,
    )
    await m.reply_text(
        strings("tmute_success").format(
            user=m.reply_to_message.from_user.mention,
            admin=m.from_user.mention,
            time=split_time[1],
        )
    )


@Client.on_message(filters.command("tban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def tban(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("error_must_specify_time").format(command=m.command[0])
        )
    split_time = m.text.split(None, 1)
    ban_time = await time_extract(m, split_time[1])
    if not ban_time:
        return
    await c.kick_chat_member(
        m.chat.id, m.reply_to_message.from_user.id, until_date=ban_time
    )

    await m.reply_text(
        strings("tban_success").format(
            user=m.reply_to_message.from_user.mention,
            admin=m.from_user.mention,
            time=split_time[1],
        )
    )


@Client.on_message(filters.command("purge", prefix))
@require_admin(permissions=["can_delete_messages"], allow_in_private=True)
@use_chat_lang()
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
                await c.delete_messages(
                    chat_id=m.chat.id, message_ids=message_ids, revoke=True
                )
                count_del_etion_s += len(message_ids)
                message_ids = []
        if len(message_ids) > 0:
            await c.delete_messages(
                chat_id=m.chat.id, message_ids=message_ids, revoke=True
            )
            count_del_etion_s += len(message_ids)
    await status_message.edit_text(
        strings("purge_success").format(count=count_del_etion_s)
    )
    await asyncio.sleep(5)
    await status_message.delete()


@Client.on_message(filters.command("antichannelpin", prefix))
@require_admin(permissions=["can_pin_messages"])
@use_chat_lang()
async def setantichannelpin(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        if m.command[1] == "on":
            await toggle_antichannelpin(m.chat.id, True)
            await m.reply_text(strings("antichannelpin_enabled"))
        elif m.command[1] == "off":
            await toggle_antichannelpin(m.chat.id, False)
            await m.reply_text(strings("antichannelpin_disabled"))
        else:
            await m.reply_text(strings("antichannelpin_invalid_arg"))
    else:
        check_acp = await check_if_antichannelpin(m.chat.id)
        if not check_acp:
            await m.reply_text(strings("antichannelpin_status_disabled"))
        else:
            await m.reply_text(strings("antichannelpin_status_enabled"))


@Client.on_message(filters.linked_channel, group=-1)
async def acp_action(c: Client, m: Message):
    get_acp = await check_if_antichannelpin(m.chat.id)
    getmychatmember = await c.get_chat_member(m.chat.id, "me")
    if (get_acp and getmychatmember.can_pin_messages) is True:
        await m.unpin()
    else:
        pass


@Client.on_message(filters.command("cleanservice", prefix))
@require_admin(permissions=["can_delete_messages"])
@use_chat_lang()
async def delservice(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        if m.command[1] == "on":
            await toggle_del_service(m.chat.id, True)
            await m.reply_text(strings("cleanservice_enabled"))
        elif m.command[1] == "off":
            await toggle_del_service(m.chat.id, False)
            await m.reply_text(strings("cleanservice_disabled"))
        else:
            await m.reply_text(strings("cleanservice_invalid_arg"))
    else:
        check_delservice = await check_if_del_service(m.chat.id)
        if check_delservice is None:
            await m.reply_text(strings("cleanservice_status_disabled"))
        elif check_delservice is not None:
            await m.reply_text(strings("cleanservice_status_enabled"))


@Client.on_message(filters.service, group=-1)
async def delservice_action(c: Client, m: Message):
    get_delservice = await check_if_del_service(m.chat.id)
    getmychatmember = await c.get_chat_member(m.chat.id, "me")
    if (get_delservice and getmychatmember.can_delete_messages) is True:
        await m.delete()
    else:
        pass


commands.add_command("antichannelpin", "admin")
commands.add_command("ban", "admin")
commands.add_command("cleanservice", "admin")
commands.add_command("kick", "admin")
commands.add_command("mute", "admin")
commands.add_command("pin", "admin")
commands.add_command("purge", "admin")
commands.add_command("tban", "admin")
commands.add_command("tmute", "admin")
commands.add_command("unban", "admin")
commands.add_command("unmute", "admin")
commands.add_command("unpin", "admin")
commands.add_command("unpinall", "admin")
