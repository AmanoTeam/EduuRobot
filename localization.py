import json
import os.path
from glob import glob
from typing import List, Dict
from dbh import dbc, db
from utils import group_types
from pyrogram.types import CallbackQuery


enabled_locales = [
    "en-GB",   # English
    "en-US",   # English (United States)
    "es-ES",   # Spanish
    "he-IL",   # Hebrew
    "it-IT",   # Italian
    "pt-BR",   # Portuguese (Brazil)
    "pt-BR2",  # Portuguese (Brazil, informal version)
    "ru-RU",   # Russian
    "tr-TR"    # Turkish
]


def set_lang(chat_id: int, chat_type: str, lang_code: str):
    if chat_type == "private":
        dbc.execute("UPDATE users SET chat_lang = ? WHERE user_id = ?", (lang_code, chat_id))
        db.commit()
    elif chat_type in group_types: # groups and supergroups share the same table
        dbc.execute("UPDATE groups SET chat_lang = ? WHERE chat_id = ?", (lang_code, chat_id))
        db.commit()
    elif chat_type == "channel":
        dbc.execute("UPDATE channels SET chat_lang = ? WHERE chat_id = ?", (lang_code, chat_id))
        db.commit()
    else:
        raise TypeError("Unknown chat type '%s'." % chat_type)


def get_lang(chat_id: int, chat_type: str) -> str:
    if chat_type == "private":
        dbc.execute("SELECT chat_lang FROM users WHERE user_id = ?", (chat_id,))
        ul = dbc.fetchone()
    elif chat_type in group_types: # groups and supergroups share the same table
        dbc.execute("SELECT chat_lang FROM groups WHERE chat_id = ?", (chat_id,))
        ul = dbc.fetchone()
    elif chat_type == "channel":
        dbc.execute("SELECT chat_lang FROM channels WHERE chat_id = ?", (chat_id,))
        ul = dbc.fetchone()
    else:
        raise TypeError("Unknown chat type '%s'." % chat_type)
    return ul[0] if ul else None


def cache_localizations(files: List[str]) -> Dict[str, Dict[str, str]]:
    ldict = {lang: {} for lang in enabled_locales}
    for file in files:
        lname = file.split(os.path.sep)[1]
        dic = json.load(open(file, encoding="utf-8"))
        ldict[lname].update(dic)
    return ldict


jsons: List[str] = []

for locale in enabled_locales:
    jsons += glob(os.path.join("locales", locale, "*.json"))

langdict = cache_localizations(jsons)


class GetLang:
    def __init__(self, msg):
        if isinstance(msg, CallbackQuery):
            chat = msg.message.chat
        else:
            chat = msg.chat

        lang = get_lang(chat.id, chat.type)
        if chat.type == "private":
            self.lang = lang or msg.from_user.language_code or "en-GB"
        else:
            self.lang = lang or "en-GB"
        # User has a language_code without hyphen
        if len(self.lang.split("-")) == 1:
            # Try to find a language that starts with the provided language_code
            for locale_ in enabled_locales:
                if locale_.startswith(self.lang):
                    self.lang = locale_
        elif self.lang.split("-")[1].islower():
            self.lang = self.lang.split("-")
            self.lang[1] = self.lang[1].upper()
            self.lang = "-".join(self.lang)
        self.lang = self.lang if self.lang in enabled_locales else "en-GB"

        self.dic = langdict.get(self.lang, langdict["en-GB"])

    def strs(self, string):
        return self.dic.get(string) or langdict["en-GB"].get(string) or string
