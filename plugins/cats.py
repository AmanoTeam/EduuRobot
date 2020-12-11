from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from localization import use_chat_lang
from consts import http


@Client.on_message(filters.command("cat", prefix))
@use_chat_lang()
async def cat(c: Client, m: Message, strings):
    r = await http.get("https://api.thecatapi.com/v1/images/search")
    rj = r.json()

    await m.reply_photo(rj[0]["url"], caption=strings("meow"))
