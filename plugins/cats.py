import aiohttp

from pyrogram import Client, Filters

from config import prefix
from localization import GetLang

@Client.on_message(Filters.command("cat", prefix))
async def cat(client, message):
    _ = GetLang(message).strs
    async with aiohttp.ClientSession() as http:
        r = await http.request("GET", "https://aws.random.cat/meow")
        rj = await r.json()

    await message.reply_photo(rj["file"], caption=_("cats.meow"))
