from datetime import datetime

from pyrogram import Client, Filters, Message

from config import prefix


@Client.on_message(Filters.command("ping", prefix))
async def ping(c: Client, m: Message):
    first = datetime.now()
    sent = await m.reply_text("**Pong!**")
    second = datetime.now()
    await sent.edit_text(f"**Pong!** `{(second - first).microseconds / 1000}`ms")
