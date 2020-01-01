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

import re

import aiohttp
from io import BytesIO
from config import bot


async def prints(msg):
    if msg.get('text'):
        if msg['text'].startswith('/print ') or msg['text'].startswith('!print '):
            if 'fullpage ' in msg['text']:
                sent = await bot.sendMessage(msg['chat']['id'], 'Tirando print...',
                                             reply_to_message_id=msg['message_id'])
                if re.match(r'^[a-z]+://', msg['text'][7:]):
                    url = msg['text'][7:]
                else:
                    url = 'http://' + msg['text'][7:]
                async with aiohttp.ClientSession() as session:
                    r = await session.post("https://api.thumbnail.ws/api/ab45a17344aa033247137cf2d457fc39ee4e7e16a464/thumbnail/get", data=dict(url=url.replace('fullpage ',''),width=1280, refresh='true', fullpage='true'))
                    req = await r.read()

                if r.status == 200:
                    file = BytesIO(req)
                    file.name = "screenshot.png"

                    await bot.sendPhoto(msg['chat']['id'], file,
                                        reply_to_message_id=msg['message_id'])
                    await bot.deleteMessage((msg['chat']['id'], sent['message_id']))
                else:
                    text = re.sub(r"<.+?>", "", req.decode())
                    await bot.editMessageText((msg['chat']['id'], sent['message_id']), "Erro:\n" + text)
                return True
            else:
                sent = await bot.sendMessage(msg['chat']['id'], 'Tirando print...',
                                             reply_to_message_id=msg['message_id'])
                if re.match(r'^[a-z]+://', msg['text'][7:]):
                    url = msg['text'][7:]
                else:
                    url = 'http://' + msg['text'][7:]
                async with aiohttp.ClientSession() as session:
                    r = await session.post("http://amn-api.herokuapp.com/print", data=dict(q=url))
                    req = await r.read()

                if r.status == 200:
                    file = BytesIO(req)
                    file.name = "screenshot.png"

                    await bot.sendPhoto(msg['chat']['id'], file,
                                        reply_to_message_id=msg['message_id'])
                    await bot.deleteMessage((msg['chat']['id'], sent['message_id']))
                else:
                    text = re.sub(r"<.+?>", "", req.decode())
                    await bot.editMessageText((msg['chat']['id'], sent['message_id']), "Erro:\n" + text)
                return True
