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

import os
import html
import aiohttp
import time
import zipfile
from aiohttp.client_exceptions import ContentTypeError


async def send_to_dogbin(text):
    if not isinstance(text, bytes):
        text = text.encode()
    async with aiohttp.ClientSession() as session:
        post = await session.post("https://del.dog/documents", data=text)
        try:
            json = await post.json()
            return "https://del.dog/" + json["key"]
        except ContentTypeError:
            text = await post.text()
            return html.escape(text)

async def send_to_hastebin(text):
    if not isinstance(text, bytes):
        text = text.encode()
    async with aiohttp.ClientSession() as session:
        post = await session.post("https://haste.thevillage.chat/documents", data=text)
        try:
            json = await post.json()
            return "https://haste.thevillage.chat/" + json["key"]
        except ContentTypeError:
            text = await post.text()
            return html.escape(text)


def pretty_size(size):
    units = ['B', 'KB', 'MB', 'GB']
    unit = 0
    while size >= 1024:
        size /= 1024
        unit += 1
    return '%0.2f %s' % (size, units[unit])


def get_flag(code):
    offset = 127462 - ord('A')
    return chr(ord(code[0]) + offset) + chr(ord(code[1]) + offset)


def escape_markdown(text):
    text = text.replace('[', '\[')
    text = text.replace('_', '\_')
    text = text.replace('*', '\*')
    text = text.replace('`', '\`')

    return text

def backup_sources(output_file=None):
    ctime = int(time.time())

    if isinstance(output_file, str) and not output_file.lower().endswith('.zip'):
        output_file += '.zip'

    fname = output_file or 'backup-{}.zip'.format(ctime)

    with zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED) as backup:
        for folder, _, files in os.walk('.'):
            for file in files:
                if file != fname and not file.endswith('.pyc') and '.heroku' not in folder.split('/') and 'dls' not in folder.split('/'):
                    backup.write(os.path.join(folder, file))

    return fname
