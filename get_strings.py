from db_handler import cursor
from glob import glob
import json


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
                self.language = cursor.fetchall()[0][0]
            except IndexError:
                self.language = 'en'
        else:
            cursor.execute('SELECT chat_lang FROM users WHERE user_id = ?', (chat_id,))
            try:
                self.language = cursor.fetchall()[0][0]
            except IndexError:
                self.language = 'en'

        self.strings = strings[self.language]


    def get(self, string_key):
        if strings[self.language].get(string_key):
            return strings[self.language][string_key]
        elif strings['en'].get(string_key):
            return strings['en'][string_key]
        else:
            return string_key