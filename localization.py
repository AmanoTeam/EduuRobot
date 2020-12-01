import json
import inspect
import os.path
from functools import wraps, partial
from glob import glob
from typing import List, Dict
from dbh import dbc, db
from utils import group_types
from pyrogram.types import CallbackQuery


enabled_locales = [
    "ar-SA",   # Arabic
    "de-DE",   # German
    "en-GB",   # English
    "en-US",   # English (United States)
    "es-ES",   # Spanish
    "fr-FR",   # French
    "he-IL",   # Hebrew
    "id-ID",   # Indonesian
    "it-IT",   # Italian
    "ja-JP",   # Japanese
    "pt-BR",   # Portuguese (Brazil)
    "pt-BR2",  # Portuguese (Brazil, informal version)
    "ru-RU",   # Russian
    "tr-TR",   # Turkish
    "zh-CN",   # Chinese (Simplified)
]

default_language = "en-GB"


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
        _, lname, pname = file.split(os.path.sep)
        pname = pname.split(".")[0]
        dic = json.load(open(file, encoding="utf-8"))
        dic.update(ldict[lname].get(pname, {}))
        ldict[lname][pname] = dic
    return ldict


jsons: List[str] = []

for locale in enabled_locales:
    jsons += glob(os.path.join("locales", locale, "*.json"))

langdict = cache_localizations(jsons)


def get_locale_string(dic: dict, language: str, key: str, context: str = None) -> str:
    if context:
        dic = langdict[language][context]
    return dic.get(key) or langdict[default_language].get(key) or key


def use_chat_lang(func):
    frame = inspect.stack()[1]
    filename = frame[0].f_code.co_filename.split(os.path.sep)[-1].split(".")[0]

    @wraps(func)
    async def wrapper(client, message):
        if isinstance(message, CallbackQuery):
            chat = message.message.chat
        else:
            chat = message.chat

        lang = get_lang(chat.id, chat.type)
        if chat.type == "private":
            lang = lang or message.from_user.language_code or default_language
        else:
            lang = lang or default_language
        # User has a language_code without hyphen
        if len(lang.split("-")) == 1:
            # Try to find a language that starts with the provided language_code
            for locale_ in enabled_locales:
                if locale_.startswith(lang):
                    lang = locale_
        elif lang.split("-")[1].islower():
            lang = lang.split("-")
            lang[1] = lang[1].upper()
            lang = "-".join(lang)
        lang = lang if lang in enabled_locales else default_language

        dic = langdict.get(lang, langdict[default_language])

        lfunc = partial(get_locale_string, dic.get(filename), lang)
        return await func(client, message, lfunc)
    return wrapper
