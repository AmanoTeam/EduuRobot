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
import json
from io import BytesIO

from config import bot, bot_username


async def jsondump(msg):
    if msg.get('text'):
        if msg['text'].startswith('/jsondump') or msg['text'].startswith('!jsondump') or msg[
            'text'] == '/jsondump@' + bot_username:
            msgjson = json.dumps(msg, indent=2, sort_keys=False)
            if '-f' not in msg['text'] and len(msgjson) < 4080:
                await bot.sendMessage(msg['chat']['id'], '<pre>' + html.escape(msgjson) + '</pre>',
                                      'html', reply_to_message_id=msg['message_id'])
            else:
                await bot.sendChatAction(msg['chat']['id'], 'upload_document')
                file = BytesIO(msgjson.encode())
                file.name = "dump.json"
                await bot.sendDocument(msg['chat']['id'], file,
                                       reply_to_message_id=msg['message_id'])
            return True
