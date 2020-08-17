import aiohttp

from pyrogram import Client, Filters, Message

from config import prefix
from localization import GetLang


@Client.on_message(Filters.command("cat", prefix))
async def cat(c: Client, m: Message):
    _ = GetLang(m).strs
    async with aiohttp.ClientSession() as http:
        r = await http.request("GET", "https://api.thecatapi.com/v1/images/search")
        rj = await r.json()

    await m.reply_photo(rj[0]["url"], caption=_("cats.meow"))
