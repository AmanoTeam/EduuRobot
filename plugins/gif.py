import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from localization import use_chat_lang
from utils import http
from config import TENOR_API_KEY, prefix


if not TENOR_API_KEY:
    logging.warning(f"[{__name__}] You need to fill TENOR_API_KEY in your config file in order to use this plugin.")


@Client.on_message(filters.command("gif", prefix))
@use_chat_lang
async def gif(c: Client, m: Message, strings):
    text = m.text[5:]
    r = await http.get("https://api.tenor.com/v1/random",
                       params=dict(q=text, key=TENOR_API_KEY, limit=1))
    rjson = r.json()
    if rjson["results"]:
        res = rjson["results"][0]["media"][0]["mediumgif"]["url"]
        await m.reply_animation(res)
    else:
        await m.reply_text(strings("no_results", context="general"))

