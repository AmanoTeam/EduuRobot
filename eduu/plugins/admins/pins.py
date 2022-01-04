from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands, require_admin


@Client.on_message(filters.command("pin", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def pin(c: Client, m: Message):
    disable_notifications = "loud" not in m.text

    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id,
        disable_notification=disable_notifications,
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


commands.add_command("pin", "admin")
commands.add_command("unpin", "admin")
commands.add_command("unpinall", "admin")
