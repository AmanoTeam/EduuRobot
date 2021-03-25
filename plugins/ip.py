from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from consts import http
import re

@Client.on_message(filters.command("ip", prefix))
async def ip_cmd(c: Client, m: Message):
    if len(m.text.split()) > 1:
        text = m.text.split(maxsplit=1)[1]
        if text.startswith("http"):
            url = re.sub("http(s|)://", "", text)
        else:
            url = text
        r = await http.get('http://ip-api.com/json/' + url)
        req = r.json()
        x = ""
        for i in req:
            x += "<b>{}</b>: <code>{}</code>\n".format(i.title(), req[i])
        await m.reply_text(x, parse_mode="html")
    else:
        await m.reply_text("You must specify the url, E.g.: <code>/ip example.com</code>")
