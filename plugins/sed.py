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
import regex

from config import bot


async def sed(msg):
    if msg.get('text'):
        if regex.match(r's/(.+)?/(.+)?(/.+)?', msg['text']) and msg.get('reply_to_message'):
            exp = regex.split(r'(?<![^\\]\\)/', msg['text'])
            pattern = exp[1]
            replace_with = exp[2].replace(r'\/', '/')
            flags = exp[3] if len(exp) > 3 else ''

            count = 1
            rflags = 0

            if 'g' in flags:
                count = 0
            if 'i' in flags and 's' in flags:
                rflags = regex.I | regex.S
            elif 'i' in flags:
                rflags = regex.I
            elif 's' in flags:
                rflags = regex.S

            if msg['reply_to_message'].get('text'):
                text = msg['reply_to_message']['text']
            elif msg['reply_to_message'].get('caption'):
                text = msg['reply_to_message']['caption']
            else:
                return

            try:
                res = regex.sub(pattern, replace_with, text, count=count, flags=rflags, timeout=1)
            except TimeoutError:
                await bot.sendMessage(msg['chat']['id'], 'Ops, o seu regex executou por muito tempo.',
                                          reply_to_message_id=msg['message_id'])
            except regex.error as e:
                await bot.sendMessage(msg['chat']['id'], "Erro: " + str(e),
                                      reply_to_message_id=msg['message_id'])
            else:
                await bot.sendMessage(msg['chat']['id'], f'<pre>{html.escape(res)}</pre>', 'html',
                                      reply_to_message_id=msg['reply_to_message']['message_id'])

            return True
