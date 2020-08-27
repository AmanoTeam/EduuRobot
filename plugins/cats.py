import httpx

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from localization import GetLang


@Client.on_message(filters.command("cat", prefix))
async def cat(c: Client, m: Message):
    _ = GetLang(m).strs
    async with httpx.AsyncClient(http2=True) as http:
        r = await http.get("https://api.thecatapi.com/v1/images/search")
        rj = r.json()

    await m.reply_photo(rj[0]["url"], caption=_("cats.meow"))
