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

from datetime import datetime

from config import bot, bot_username


async def ping(msg):
    if msg.get('text'):
        if msg['text'] == '/ping' or msg['text'] == '!ping' or msg['text'] == '/ping@' + bot_username:
            first = datetime.now()
            sent = await bot.sendMessage(msg['chat']['id'], '*Pong!*', 'Markdown',
                                         reply_to_message_id=msg['message_id'])
            second = datetime.now()
            await bot.editMessageText((msg['chat']['id'], sent['message_id']),
                                      '*Pong!* `{}`ms'.format((second - first).microseconds / 1000), 'Markdown')
            return True

        elif msg['text'] == '/king' or msg['text'] == '!king' or msg['text'] == '/king@' + bot_username:
            await bot.sendMessage(msg['chat']['id'], '*Kong!*', 'Markdown', reply_to_message_id=msg['message_id'])
            return True
