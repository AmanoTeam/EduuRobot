from config import prefix
from datetime import datetime
from pyrogram import Client, Filters


@Client.on_message(Filters.command("ping", prefix))
async def ping(client, message):
    first = datetime.now()
    sent = await message.reply("**Pong!**")
    second = datetime.now()
    await sent.edit(f"**Pong!** `{(second - first).microseconds / 1000}`ms")
