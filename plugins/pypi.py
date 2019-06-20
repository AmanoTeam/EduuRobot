# Copyright (C) 2018-2019 Amano Team <contact@amanoteam.ml>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import html
import re

import aiohttp
from amanobot.namedtuple import InlineKeyboardMarkup

from config import bot, version


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition


async def pypi(msg):
    if msg.get('text'):
        if msg['text'].startswith('/pypi ') or msg['text'].startswith('!pypi '):
            text = msg['text'][6:]
            async with aiohttp.ClientSession() as session:
                r = await session.get(f"https://pypi.python.org/pypi/{text}/json",
                                      headers={"User-Agent": "Eduu/" + version})
                json = await r.json()
            if r.status == 200:
                pypi = escape_definition(json["info"])
                message = "<b>%s</b> by <i>%s</i> (%s)\n" \
                          "Platform: <b>%s</b>\n" \
                          "Version: <b>%s</b>\n" \
                          "License: <b>%s</b>\n" \
                          "Summary: <b>%s</b>\n" % (
                              pypi["name"], pypi["author"], pypi["author_email"], pypi["platform"],
                              pypi["version"], pypi["platform"], pypi["summary"])
                return await bot.sendMessage(msg['chat']['id'], message, reply_to_message_id=msg['message_id'],
                                             parse_mode="HTML", disable_web_page_preview=True,
                                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                 [dict(text='Package home page', url=pypi['home_page'])]]))
            else:
                return await bot.sendMessage(msg['chat']['id'], f"Cant find *{text}* in pypi",
                                             reply_to_message_id=msg['message_id'], parse_mode="Markdown",
                                             disable_web_page_preview=True)
            return True
