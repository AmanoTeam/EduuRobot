import httpx

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from localization import GetLang


@Client.on_message(filters.command("dog", prefix))
async def dog(c: Client, m: Message):
    _ = GetLang(m).strs
    async with httpx.AsyncClient() as http:
        r = await http.get("https://random.dog/woof.json")
        rj = r.json()

    await m.reply_photo(rj["url"], caption=_("dogs.woof"))
