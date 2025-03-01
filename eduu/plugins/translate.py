# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import html
import re

# from gpytranslate import Translator
from hydrogram import Client, filters
from hydrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from config import PREFIXES
from eduu.utils import commands, inline_commands, http
from eduu.utils.localization import Strings, use_chat_lang

class Translator:    
    def __init__(self, base_url: str = "https://sakty-playground-twilight-leaf-8a39.ymahessa.workers.dev"):
        self.base_url = base_url
        self.headers = {'sec-fetch-site': 'same-origin', 'password': 'rahasia'}
    
    async def _request(self, endpoint: str, payload: dict):
        try:
            response = await http.post(f"{self.base_url}/{endpoint}", json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "cek": False,
                "alasan": f"HTTP error: {e.response.status_code}\n{e.response.text}"
            }
        except Exception as e:
            return {"cek": False, "alasan": str(e)}

    async def detect(self, text: str):
        """Detect the language of the provided text."""
        return await self._request("detect_trans", {"text": text})

    async def translate(self, text: str, sourcelang: str = "auto", targetlang: str = "en"):
        """Translate text from source language to target language."""
        return await self._request("google_v2_trans", {
            "text": text,
            "from": sourcelang,
            "to": targetlang
        })
            
tr = Translator()

# See https://cloud.google.com/translate/docs/languages
# fmt: off
LANGUAGES = [
    "af", "sq", "am", "ar", "hy",
    "as", "ay", "az", "bm", "eu",
    "be", "bn", "bho", "bs", "bg",
    "ca", "ceb", "zh", "co", "hr",
    "cs", "da", "dv", "doi", "nl",
    "en", "eo", "et", "ee", "fil",
    "fi", "fr", "fy", "gl", "ka",
    "de", "el", "gn", "gu", "ht",
    "ha", "haw", "he", "iw", "hi",
    "hmn", "hu", "is", "ig", "ilo",
    "id", "ga", "it", "ja", "jv",
    "jw", "kn", "kk", "km", "rw",
    "gom", "ko", "kri", "ku", "ckb",
    "ky", "lo", "la", "lv", "ln",
    "lt", "lg", "lb", "mk", "mai",
    "mg", "ms", "ml", "mt", "mi",
    "mr", "mni", "lus", "mn", "my",
    "ne", "no", "ny", "or", "om",
    "ps", "fa", "pl", "pt", "pa",
    "qu", "ro", "ru", "sm", "sa",
    "gd", "nso", "sr", "st", "sn",
    "sd", "si", "sk", "sl", "so",
    "es", "su", "sw", "sv", "tl",
    "tg", "ta", "tt", "te", "th",
    "ti", "ts", "tr", "tk", "ak",
    "uk", "ur", "ug", "uz", "vi",
    "cy", "xh", "yi", "yo", "zu"
]
# fmt: on


def get_tr_lang(text):
    if len(text.split()) > 0:
        lang = text.split()[0]
        if lang.split("-")[0] not in LANGUAGES:
            lang = "pt"
        if len(lang.split("-")) > 1 and lang.split("-")[1] not in LANGUAGES:
            lang = "pt"
    else:
        lang = "pt"
    return lang


@Client.on_message(filters.command("tr", PREFIXES))
@use_chat_lang
async def translate(c: Client, m: Message, s: Strings):
    text = m.text[4:]
    lang = get_tr_lang(text)

    text = text.replace(lang, "", 1).strip() if text.startswith(lang) else text

    if not text and m.reply_to_message:
        text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        await m.reply_text(s("tr_usage"), reply_to_message_id=m.id)
        return

    sent = await m.reply_text(s("tr_translating"), reply_to_message_id=m.id)
    langs = {}

    if len(lang.split("-")) > 1:
        langs["sourcelang"] = lang.split("-")[0]
        langs["targetlang"] = lang.split("-")[1]
    else:
        langs["targetlang"] = lang

    trres = await tr.translate(text, **langs)
    if not trres.get('cek'):
        return await sent.edit_text(f"Translation Error: {trres.get('alasan', 'error')}")
        
    text = trres.get('terjemah')

    res = html.escape(text)
    await sent.edit_text(
        s("tr_translation").format(
            source_lang=trres.lang, target_lang=langs["targetlang"], translation=res
        )
    )


@Client.on_inline_query(filters.regex(r"^tr .+", re.IGNORECASE))
@use_chat_lang
async def tr_inline(c: Client, q: InlineQuery, s: Strings):
    to_tr = q.query.split(None, 2)[2]
    source_language = await tr.detect(q.query.split(None, 2)[2])
    
    if not source_language.get('cek'):
        source_language = 'en'
    else:
        source_language = source_language['detect']
        
    target_language = q.query.lower().split()[1]
    translation = await tr.translate(to_tr, sourcelang=source_language, targetlang=target_language)
    
    if not translation.get('cek'):
        text = translation.get('alasan', 'error')
    else:
        text = translation.get('terjemah')
        
    await q.answer([
        InlineQueryResultArticle(
            title=s("tr_inline_send").format(
                source_lang=source_language, target_lang=target_language
            ),
            description=f"{text}",
            input_message_content=InputTextMessageContent(f"{text}"),
        )
    ])


commands.add_command("tr", "tools")
inline_commands.add_command("tr <lang> <text>")
