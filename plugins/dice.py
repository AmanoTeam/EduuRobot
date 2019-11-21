import random

from pyrogram import Client, Filters

from config import prefix


@Client.on_message(Filters.command(["dice", "dados"], prefix))
async def dice(client, message):
    dicen = random.randint(1, 6)
    await message.reply_text("🎲 The dice stopped at the number: {number}".format(
        number=dicen
    ))
