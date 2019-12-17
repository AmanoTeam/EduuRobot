import aiohttp

from pyrogram import Client, Filters

from config import prefix
from localization import GetLang


@Client.on_message(Filters.command("dog", prefix))
async def dog(client, message):
    _ = GetLang(message).strs
    async with aiohttp.ClientSession() as http:
        r = await http.request("GET", "https://random.dog/woof.json")
        rj = await r.json()

    await message.reply_photo(rj["url"], caption=_("dogs.woof"))
