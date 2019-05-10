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

import json
from glob import glob

from db_handler import cursor

strings = {}
langs = [x.split('/')[1] for x in glob('langs/*/main.json')]

for lang in langs:
    strings[lang] = {}
    for file in glob('langs/{}/*.json'.format(lang)):
        strings[lang].update(json.load(open(file)))


class Strings:
    def __init__(self, chat_id):
        # Supergoup and group IDs are negative.
        if chat_id < 0:
            cursor.execute('SELECT chat_lang FROM chats WHERE chat_id = ?', (chat_id,))
            try:
                self.language = cursor.fetchone()[0]
            except (IndexError, TypeError):
                self.language = 'en'
        else:
            cursor.execute('SELECT chat_lang FROM users WHERE user_id = ?', (chat_id,))
            try:
                self.language = cursor.fetchone()[0]
            except (IndexError, TypeError):
                self.language = 'en'
        if self.language not in langs:
            self.language = 'en'

        self.strings = strings[self.language]

    def get(self, string_key):
        if strings[self.language].get(string_key):
            return strings[self.language][string_key]
        elif strings['en'].get(string_key):
            return strings['en'][string_key]
        else:
            return string_key
