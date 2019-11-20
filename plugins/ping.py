from datetime import datetime

from pyrogram import Client, Filters

from config import prefix


@Client.on_message(Filters.command("ping", prefix))
async def ping(client, message):
    first = datetime.now()
    sent = await message.reply_text("**Pong!**")
    second = datetime.now()
    await sent.edit(f"**Pong!** `{(second - first).microseconds / 1000}`ms")
