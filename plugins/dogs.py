from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from localization import use_chat_lang
from consts import http


@Client.on_message(filters.command("dog", prefix))
@use_chat_lang()
async def dog(c: Client, m: Message, strings):
    r = await http.get("https://random.dog/woof.json")
    rj = r.json()

    await m.reply_photo(rj["url"], caption=strings("woof"))
