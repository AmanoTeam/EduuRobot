# Copyright (C) 2018-2020 Amano Team <contact@amanoteam.com>
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

from config import bot


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
                r = await session.get(f"https://pypi.org/pypi/{text}/json",
                                      headers={"Accept-Encoding": "gzip"})
                if r.status == 200:
                    json = await r.json()
                    pypi_info = escape_definition(json["info"])
                    message = "<b>%s</b> by <i>%s %s</i>\n" \
                              "Platform: <b>%s</b>\n" \
                              "Version: <b>%s</b>\n" \
                              "License: <b>%s</b>\n" \
                              "Summary: <b>%s</b>\n" % (
                                  pypi_info["name"], pypi_info["author"], f"&lt;{pypi_info['author_email']}&gt;" if pypi_info['author_email'] else "",
                                  pypi_info["platform"] or "Not specified", pypi_info["version"], pypi_info["license"] or "None", pypi_info["summary"])
                    if pypi_info['home_page'] and pypi_info['home_page'] != "UNKNOWN":
                        kb = InlineKeyboardMarkup(inline_keyboard=[
                                                  [dict(text='Package home page', url=pypi_info['home_page'])]])
                    else:
                        kb = None
                    await bot.sendMessage(msg['chat']['id'], message, reply_to_message_id=msg['message_id'],
                                          parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb)
                else:
                    await bot.sendMessage(msg['chat']['id'], f"Cant find *{text}* in pypi (Returned code was {r.status})",
                                          reply_to_message_id=msg['message_id'], parse_mode="Markdown",
                                          disable_web_page_preview=True)
            return True
