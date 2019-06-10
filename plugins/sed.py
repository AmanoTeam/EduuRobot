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

import ctypes
import html
import re
from multiprocessing import Process, Manager

from config import bot


def replace(res, pattern, replace_with, text, count, rflags):
    res.value = re.sub(pattern, replace_with, text, count=count, flags=rflags)


async def sed(msg):
    if msg.get('text'):
        if re.match(r's/(.+)?/(.+)?(/.+)?', msg['text']) and msg.get('reply_to_message'):
            exp = re.split(r'(?<![^\\]\\)/', msg['text'])
            pattern = exp[1]
            replace_with = exp[2]
            flags = exp[3] if len(exp) > 3 else ''

            count = 1
            rflags = 0

            if 'g' in flags:
                count = 0
            if 'i' in flags and 's' in flags:
                rflags = re.I | re.S
            elif 'i' in flags:
                rflags = re.I
            elif 's' in flags:
                rflags = re.S

            if msg['reply_to_message'].get('text'):
                text = msg['reply_to_message']['text']
            elif msg['reply_to_message'].get('caption'):
                text = msg['reply_to_message']['caption']
            else:
                return

            manager = Manager()
            res = manager.Value(ctypes.c_char_p, None)

            p = Process(target=replace, args=(res, pattern, replace_with, text, count, rflags))
            p.start()
            p.join(0.2)
            p.terminate()

            if res.value is None:
                await bot.sendMessage(msg['chat']['id'], 'Ocorreu um erro com o seu padrão regex.',
                                      reply_to_message_id=msg['message_id'])
            else:
                await bot.sendMessage(msg['chat']['id'], f'<pre>{html.escape(res.value)}</pre>', 'html',
                                      reply_to_message_id=msg['reply_to_message']['message_id'])

            return True
