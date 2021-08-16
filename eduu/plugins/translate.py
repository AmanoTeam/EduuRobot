# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import html

from gpytranslate import Translator
from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from eduu.config import prefix
from eduu.utils import commands
from eduu.utils.localization import use_chat_lang
from eduu.utils.bot_error_log import logging_errors

tr = Translator()

# See https://cloud.google.com/translate/docs/languages
# fmt: off
LANGUAGES = [
    "af", "sq", "am", "ar", "hy",
    "az", "eu", "be", "bn", "bs",
    "bg", "ca", "ceb", "zh", "co",
    "hr", "cs", "da", "nl", "en",
    "eo", "et", "fi", "fr", "fy",
    "gl", "ka", "de", "el", "gu",
    "ht", "ha", "haw", "he", "iw",
    "hi", "hmn", "hu", "is", "ig",
    "id", "ga", "it", "ja", "jv",
    "kn", "kk", "km", "rw", "ko",
    "ku", "ky", "lo", "la", "lv",
    "lt", "lb", "mk", "mg", "ms",
    "ml", "mt", "mi", "mr", "mn",
    "my", "ne", "no", "ny", "or",
    "ps", "fa", "pl", "pt", "pa",
    "ro", "ru", "sm", "gd", "sr",
    "st", "sn", "sd", "si", "sk",
    "sl", "so", "es", "su", "sw",
    "sv", "tl", "tg", "ta", "tt",
    "te", "th", "tr", "tk", "uk",
    "ur", "ug", "uz", "vi", "cy",
    "xh", "yi", "yo", "zu",
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


@Client.on_message(filters.command("tr", prefix))
@use_chat_lang()
@logging_errors
async def translate(c: Client, m: Message, strings):
    text = m.text[4:]
    lang = get_tr_lang(text)

    text = text.replace(lang, "", 1).strip() if text.startswith(lang) else text

    if not text and m.reply_to_message:
        text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        return await m.reply_text(
            strings("translate_usage"), reply_to_message_id=m.message_id
        )

    sent = await m.reply_text(strings("translating"), reply_to_message_id=m.message_id)
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


@Client.on_inline_query(filters.regex(r"^tr"))
@use_chat_lang()
async def tr_inline(c: Client, q: InlineQuery, strings):
    try:
        to_tr = q.query.split(None, 2)[2]
        source_language = await tr.detect(q.query.split(None, 2)[2])
        to_language = q.query.lower().split()[1]
        translation = await tr(
            to_tr, sourcelang=source_language, targetlang=to_language
        )
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=strings("translate_inline_send").format(
                        srclangformat=source_language, tolangformat=to_language
                    ),
                    description=f"{translation.text}",
                    input_message_content=InputTextMessageContent(
                        f"{translation.text}"
                    ),
                )
            ]
        )
    except IndexError:
        return


commands.add_command("tr", "tools")
