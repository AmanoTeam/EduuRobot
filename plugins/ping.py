from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix


@Client.on_message(filters.command("ping", prefix))
async def ping(c: Client, m: Message):
    first = datetime.now()
    sent = await m.reply_text("**Pong!**")
    second = datetime.now()
    await sent.edit_text(f"**Pong!** `{(second - first).microseconds / 1000}`ms")
