import random

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from localization import use_chat_lang
from consts import http


@Client.on_message(filters.command("coub", prefix))
@use_chat_lang()
async def coub(c: Client, m: Message, strings):
    text = m.text[6:]
    r = await http.get("https://coub.com/api/v2/search/coubs",
                       params=dict(q=text))
    rjson = r.json()
    try:
        content = random.choice(rjson["coubs"])
        links = content["permalink"]
        title = content["title"]
    except IndexError:
        await m.reply_text(strings("no_results", context="general"))
    else:
        await m.reply_text(f"**[{title}](https://coub.com/v/{links})**")
