# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import html
import re

from gpytranslate import Translator
from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from config import PREFIXES
from eduu.utils import commands, inline_commands
from eduu.utils.localization import use_chat_lang

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
async def translate(c: Client, m: Message, strings):
    text = m.text[4:]
    lang = get_tr_lang(text)

    text = text.replace(lang, "", 1).strip() if text.startswith(lang) else text

    if not text and m.reply_to_message:
        text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        return await m.reply_text(strings("translate_usage"), reply_to_message_id=m.id)

    sent = await m.reply_text(strings("translating"), reply_to_message_id=m.id)
    langs = {}

    if len(lang.split("-")) > 1:
        langs["sourcelang"] = lang.split("-")[0]
        langs["targetlang"] = lang.split("-")[1]
    else:
        langs["targetlang"] = lang

    trres = await tr.translate(text, **langs)
    text = trres.text

    res = html.escape(text)
    await sent.edit_text(
        strings("translation").format(
            from_lang=trres.lang, to_lang=langs["targetlang"], translation=res
        )
    )
    return None


@Client.on_inline_query(filters.regex(r"^tr .+", re.I))
@use_chat_lang
async def tr_inline(c: Client, q: InlineQuery, strings):
    to_tr = q.query.split(None, 2)[2]
    source_language = await tr.detect(q.query.split(None, 2)[2])
    to_language = q.query.lower().split()[1]
    translation = await tr(to_tr, sourcelang=source_language, targetlang=to_language)
    await q.answer(
        [
            InlineQueryResultArticle(
                title=strings("translate_inline_send").format(
                    srclangformat=source_language, tolangformat=to_language
                ),
                description=f"{translation.text}",
                input_message_content=InputTextMessageContent(f"{translation.text}"),
            )
        ]
    )


commands.add_command("tr", "tools")
inline_commands.add_command("tr <lang> <text>")
