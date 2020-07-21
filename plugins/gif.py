import random
import aiohttp
import logging

from pyrogram import Client, Filters, Message

from localization import GetLang
from config import GIPHY_API_KEY, prefix


if not GIPHY_API_KEY:
    logging.warning(f"[{__name__}] You need to fill GIPHY_API_KEY in your config file in order to use this plugin.")


@Client.on_message(Filters.command("gif", prefix))
async def gif(c: Client, m: Message):
    _ = GetLang(m).strs
    text = m.text[5:]
    async with aiohttp.ClientSession() as session:
        r = await session.get("http://api.giphy.com/v1/gifs/search",
                              params=dict(q=text, api_key=GIPHY_API_KEY, limit=7))
        rjson = await r.json()
    if rjson["data"]:
        res = random.choice(rjson["data"])
        result = res["images"]["downsized_medium"]["url"]
        await m.reply_animation(result)
    else:
        await m.reply_text(_("general.no_results"))

