import aiohttp

from pyrogram import Client, Filters, Message

from config import prefix
from localization import GetLang


@Client.on_message(Filters.command("cat", prefix))
async def cat(c: Client, m: Message):
    _ = GetLang(m).strs
    async with aiohttp.ClientSession() as http:
        r = await http.request("GET", "https://aws.random.cat/meow")
        rj = await r.json()

    await m.reply_photo(rj["file"], caption=_("cats.meow"))
