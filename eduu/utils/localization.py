# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from __future__ import annotations

import json
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from hydrogram.enums import ChatType
from hydrogram.types import CallbackQuery, InlineQuery, Message

from eduu.database.localization import get_db_lang

if TYPE_CHECKING:
    from collections.abc import Callable

enabled_locales: list[str] = [
    "en-GB",  # English (United Kingdom)
    "en-US",  # English (United States)
    "pt-BR",  # Portuguese (Brazil)
    "es-ES",  # Spanish
    "fr-FR",  # French
    "de-DE",  # German
    "it-IT",  # Italian
    "nl-NL",  # Dutch
    "ar-SA",  # Arabic
    "ckb-IR",  # Sorani (Kurdish)
    "fi-FI",  # Finnish
    "he-IL",  # Hebrew
    "id-ID",  # Indonesian
    "ja-JP",  # Japanese
    "no-NO",  # Norwegian
    "pl-PL",  # Polish
    "pt-BRe",  # Portuguese (Brazil, extended version)
    "pt-BR2",  # Portuguese (Brazil, informal version)
    "ro-RO",  # Romanian
    "ru-RU",  # Russian
    "sv-SE",  # Swedish
    "tr-TR",  # Turkish
    "uk-UA",  # Ukranian
    "zh-CN",  # Chinese (Simplified)
    "zh-TW",  # Chinese (Traditional)
]

default_language: str = "en-GB"


def cache_localizations(files: list[Path]) -> dict[str, dict[str, str]]:
    ldict = {lang: {} for lang in enabled_locales}
    for file in files:
        _, lname, pname = file.parts
        pname = pname.split(".")[0]
        dic: dict = json.load(file.open("r", encoding="utf8"))
        ldict[lname].update(dic)
    return ldict


jsons: list[Path] = []

for locale in enabled_locales:
    jsons.extend((Path("locales") / locale).glob("*.json"))

langdict = cache_localizations(jsons)


def get_locale_string(
    language: str,
    key: str,
) -> str:
    res: str = langdict[language].get(key) or langdict[default_language].get(key) or key
    return res


async def get_lang(message: CallbackQuery | Message | InlineQuery) -> str:
    if isinstance(message, CallbackQuery):
        chat = message.message.chat if message.message else message.from_user
        chat_type = message.message.chat.type if message.message else ChatType.PRIVATE
    elif isinstance(message, Message):
        chat = message.chat
        chat_type = message.chat.type
    elif isinstance(message, InlineQuery):
        chat = message.from_user
        chat_type = ChatType.PRIVATE
    else:
        raise TypeError(f"Update type '{message.__name__}' is not supported.")

    lang = await get_db_lang(chat.id, chat_type)

    if chat_type == ChatType.PRIVATE:
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
    return lang if lang in enabled_locales else default_language


def use_chat_lang(func: Callable):
    """Decorator to get the chat language and pass it to the function."""

    async def wrapper(client, message, *args, **kwargs):
        lang = await get_lang(message)

        lfunc = partial(get_locale_string, lang)
        return await func(client, message, *args, lfunc, **kwargs)

    return wrapper
