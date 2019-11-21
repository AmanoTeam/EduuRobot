import random

from pyrogram import Client, Filters

from config import prefix
from localization import GetLang


@Client.on_message(Filters.command(["dice", "dados"], prefix))
async def dice(client, message):
    _ = GetLang(message).strs
    dicen = random.randint(1, 6)
    await message.reply_text(_("dice.result").format(
        number=dicen
    ))
