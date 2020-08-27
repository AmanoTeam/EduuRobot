import random
import httpx

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from localization import GetLang


@Client.on_message(filters.command("coub", prefix))
async def coub(c: Client, m: Message):
    _ = GetLang(m).strs
    text = m.text[6:]
    async with httpx.AsyncClient(http2=True) as http:
        r = await http.get('https://coub.com/api/v2/search/coubs',
                           params=dict(q=text))
        rjson = r.json()
    try:
        content = random.choice(rjson['coubs'])
        links = content['permalink']
        title = content['title']
    except IndexError:
        await m.reply_text(_("general.no_results"))
    else:
        await m.reply_text(f'**[{title}](https://coub.com/v/{links})**')
