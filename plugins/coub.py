import random
import aiohttp

from pyrogram import Client, Filters

from config import prefix
from localization import GetLang


@Client.on_message(Filters.command("coub", prefix))
async def coub(client, message):
    _ = GetLang(message).strs
    text = message.text[6:]
    async with aiohttp.ClientSession() as session:
        r = await session.get('https://coub.com/api/v2/search/coubs',
                              params=dict(q=text))
        rjson = await r.json()
    try:
        content = random.choice(rjson['coubs'])
        links = content['permalink']
        title = content['title']
    except IndexError:
        await message.reply_text(_("general.no_results"))
    else:
        await message.reply_text(f'**[{title}](https://coub.com/v/{links})**')
