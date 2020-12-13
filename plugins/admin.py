from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from config import prefix
from utils import require_admin, time_extract


@Client.on_message(filters.command("pin", prefix))
@require_admin(permissions=["can_pin_messages"])
async def pin(c: Client, m: Message):
    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id
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
@require_admin(permissions=["can_restrict_members"])
async def ban(c: Client, m: Message):
    await c.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)


@Client.on_message(filters.command("kick", prefix))
@require_admin(permissions=["can_restrict_members"])
async def kick(c: Client, m: Message):
    await c.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.chat.unban_member(m.reply_to_message.from_user.id)


@Client.on_message(filters.command("unban", prefix))
@require_admin(permissions=["can_restrict_members"])
async def unban(c: Client, m: Message):
    await m.chat.unban_member(m.reply_to_message.from_user.id)


@Client.on_message(filters.command("mute", prefix))
@require_admin(permissions=["can_restrict_members"])
async def mute(c: Client, m: Message):
    await c.restrict_chat_member(m.chat.id,
                                 m.reply_to_message.from_user.id,
                                 ChatPermissions(can_send_messages=False))


@Client.on_message(filters.command("unmute", prefix))
@require_admin(permissions=["can_restrict_members"])
async def unmute(c: Client, m: Message):
    await m.chat.unban_member(m.reply_to_message.from_user.id)


@Client.on_message(filters.command("tmute", prefix))
@require_admin(permissions=["can_restrict_members"])
async def tmute(c: Client, m: Message):
    if len(m.command) == 1:
        return
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


@Client.on_message(filters.command("tban", prefix))
@require_admin(permissions=["can_restrict_members"])
async def tban(c: Client, m: Message):
    if len(m.command) == 1:
        return
    split_time = m.text.split(None, 1)
    ban_time = await time_extract(m, split_time[1])
    if not ban_time:
        return
    await c.kick_chat_member(
        m.chat.id,
        m.reply_to_message.from_user.id,
        until_date=ban_time
    )
