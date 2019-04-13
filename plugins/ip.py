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

import aiohttp

from config import bot


async def ip(msg):
    if msg.get('text'):
        if msg['text'].split()[0] == '/ip' or msg['text'].split()[0] == '!ip':
            text = msg['text'][4:].split('://')[-1]
            if text == '':
                await bot.sendMessage(msg['chat']['id'], '*Uso:* `/ip IP/endereço`',
                                      parse_mode='Markdown',
                                      reply_to_message_id=msg['message_id'])
            else:
                async with aiohttp.ClientSession() as session:
                    r = await session.get('http://ip-api.com/json/' + text)
                    req = await r.json()
                x = ''
                for i in req:
                    x += "*{}*: `{}`\n".format(i.title(), req[i])
                await bot.sendMessage(msg['chat']['id'], x, 'Markdown',
                                      reply_to_message_id=msg['message_id'])
            return True
