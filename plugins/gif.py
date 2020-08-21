import httpx
import logging

from pyrogram import Client, Filters, Message

from localization import GetLang
from config import TENOR_API_KEY, prefix


if not TENOR_API_KEY:
    logging.warning(f"[{__name__}] You need to fill TENOR_API_KEY in your config file in order to use this plugin.")


@Client.on_message(Filters.command("gif", prefix))
async def gif(c: Client, m: Message):
    _ = GetLang(m).strs
    text = m.text[5:]
    async with httpx.AsyncClient() as http:
        r = await http.get("https://api.tenor.com/v1/random",
                           params=dict(q=text, key=TENOR_API_KEY, limit=1))
        rjson = r.json()
    if rjson["results"]:
        res = rjson["results"][0]["media"][0]["mediumgif"]["url"]
        await m.reply_animation(res)
    else:
        await m.reply_text(_("general.no_results"))

