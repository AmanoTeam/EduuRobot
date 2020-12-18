import asyncio

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from config import prefix
from utils import require_admin, time_extract, html_user
from localization import use_chat_lang


@Client.on_message(filters.command("pin", prefix))
@require_admin(permissions=["can_pin_messages"])
async def pin(c: Client, m: Message):
    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id,
        disable_notification=True
    )
    
    
@Client.on_message(filters.command("pin loud", prefix))
@require_admin(permissions=["can_pin_messages"])
async def pinloud(c: Client, m: Message):
    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id,
        disable_notification=False
    )


@Client.on_message(filters.command("unpin", prefix))
@require_admin(permissions=["can_pin_messages"])
async def unpin(c: Client, m: Message):
    await c.unpin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id
    )


@Client.on_message(filters.command("unpinall", prefix))
@require_admin(permissions=["can_pin_messages"])
async def unpinall(c: Client, m: Message):
    await c.unpin_all_chat_messages(
        m.chat.id
    )


@Client.on_message(filters.command("ban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def ban(c: Client, m: Message, strings):
    await c.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.reply_text(
        strings("ban_success").format(
            user=html_user(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id),
            admin=html_user(m.from_user.first_name, m.from_user.id)
        )
    )


@Client.on_message(filters.command("kick", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def kick(c: Client, m: Message, strings):
    await c.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.chat.unban_member(m.reply_to_message.from_user.id)
    await m.reply_text(
        strings("kick_success").format(
            user=html_user(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id),
            admin=html_user(m.from_user.first_name, m.from_user.id)
        )
    )


@Client.on_message(filters.command("unban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def unban(c: Client, m: Message, strings):
    await m.chat.unban_member(m.reply_to_message.from_user.id)
    await m.reply_text(
        strings("unban_success").format(
            user=html_user(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id),
            admin=html_user(m.from_user.first_name, m.from_user.id)
        )
    )


@Client.on_message(filters.command("mute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def mute(c: Client, m: Message, strings):
    await c.restrict_chat_member(m.chat.id,
                                 m.reply_to_message.from_user.id,
                                 ChatPermissions(can_send_messages=False))
    await m.reply_text(
        strings("mute_success").format(
            user=html_user(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id),
            admin=html_user(m.from_user.first_name, m.from_user.id)
        )
    )


@Client.on_message(filters.command("unmute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def unmute(c: Client, m: Message, strings):
    await m.chat.unban_member(m.reply_to_message.from_user.id)
    await m.reply_text(
        strings("unmute_success").format(
            user=html_user(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id),
            admin=html_user(m.from_user.first_name, m.from_user.id)
        )
    )


@Client.on_message(filters.command("tmute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def tmute(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("error_must_specify_time").format(command=m.command[0]))
    split_time = m.text.split(None, 1)
    mute_time = await time_extract(m, split_time[1])
    if not mute_time:
        return
    await c.restrict_chat_member(
        m.chat.id,
        m.reply_to_message.from_user.id,
        ChatPermissions(can_send_messages=False),
        until_date=mute_time
    )
    await m.reply_text(
        strings("tmute_success").format(
            user=html_user(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id),
            admin=html_user(m.from_user.first_name, m.from_user.id),
            time=split_time[1]
        )
    )


@Client.on_message(filters.command("tban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def tban(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("error_must_specify_time").format(command=m.command[0]))
    split_time = m.text.split(None, 1)
    ban_time = await time_extract(m, split_time[1])
    if not ban_time:
        return
    await c.kick_chat_member(
        m.chat.id,
        m.reply_to_message.from_user.id,
        until_date=ban_time
    )

    await m.reply_text(
        strings("tban_success").format(
            user=html_user(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id),
            admin=html_user(m.from_user.first_name, m.from_user.id),
            time=split_time[1]
        )
    )


@Client.on_message(filters.command("purge", prefix))
@require_admin(permissions=["can_delete_messages"], allow_in_private=True)
@use_chat_lang()
async def purge(c: Client, m: Message, strings):
    """ purge upto the replied message """
    status_message = await m.reply_text(strings("purge_in_progress"), quote=True)
    await m.delete()
    message_ids = []
    count_del_etion_s = 0
    if m.reply_to_message:
        for a_s_message_id in range(
            m.reply_to_message.message_id,
            m.message_id
        ):
            message_ids.append(a_s_message_id)
            if len(message_ids) == 100:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=message_ids,
                    revoke=True
                )
                count_del_etion_s += len(message_ids)
                message_ids = []
        if len(message_ids) > 0:
            await c.delete_messages(
                chat_id=m.chat.id,
                message_ids=message_ids,
                revoke=True
            )
            count_del_etion_s += len(message_ids)
    await status_message.edit_text(
        strings("purge_success").format(
            count=count_del_etion_s
        )
    )
    await asyncio.sleep(5)
    await status_message.delete()
