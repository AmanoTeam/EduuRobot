from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from utils import http
from localization import GetLang


@Client.on_message(filters.command("cat", prefix))
async def cat(c: Client, m: Message):
    _ = GetLang(m).strs
    r = await http.get("https://api.thecatapi.com/v1/images/search")
    rj = r.json()

    await m.reply_photo(rj[0]["url"], caption=_("cats.meow"))
