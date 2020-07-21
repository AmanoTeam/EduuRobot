import random
import aiohttp

from pyrogram import Client, Filters, Message

from config import prefix
from localization import GetLang


@Client.on_message(Filters.command("coub", prefix))
async def coub(c: Client, m: Message):
    _ = GetLang(m).strs
    text = m.text[6:]
    async with aiohttp.ClientSession() as session:
        r = await session.get('https://coub.com/api/v2/search/coubs',
                              params=dict(q=text))
        rjson = await r.json()
    try:
        content = random.choice(rjson['coubs'])
        links = content['permalink']
        title = content['title']
    except IndexError:
        await m.reply_text(_("general.no_results"))
    else:
        await m.reply_text(f'**[{title}](https://coub.com/v/{links})**')
