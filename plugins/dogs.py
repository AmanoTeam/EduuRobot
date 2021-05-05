from config import prefix
from pyrogram import Client, filters
from pyrogram.types import Message

from consts import http
from localization import use_chat_lang
from utils import commands


@Client.on_message(filters.command("dog", prefix))
@use_chat_lang()
async def dog(c: Client, m: Message, strings):
    r = await http.get("https://random.dog/woof.json")
    rj = r.json()

    await m.reply_photo(rj["url"], caption=strings("woof"))


commands.add_command("dog", "general")
