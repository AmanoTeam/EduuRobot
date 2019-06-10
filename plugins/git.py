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


async def git(msg):
    if msg.get('text'):
        if msg['text'].startswith('/git ') or msg['text'].startswith('!git '):
            text = msg['text'][5:]
            async with aiohttp.ClientSession() as session:
                req = await session.get('https://api.github.com/users/' + text)
                res = await req.json()
            if not res.get('login'):
                return await bot.sendMessage(msg['chat']['id'], 'Usuário "{}" não encontrado.'.format(text),
                                             reply_to_message_id=msg['message_id'])
            else:
                await bot.sendMessage(msg['chat']['id'], f'''*Nome:* `{res["name"]}`
*Login:* `{res["login"]}`
*Localização:* `{res["location"]}`
*Tipo:* `{res["type"]}`
*Bio:* `{res["bio"]}`''', 'Markdown',
                                      reply_to_message_id=msg['message_id'])
            return True
