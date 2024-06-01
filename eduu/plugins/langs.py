# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from itertools import zip_longest
from typing import Union

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import PREFIXES
from eduu.database.localization import set_db_lang
from eduu.utils.decorators import require_admin
from eduu.utils.localization import langdict, use_chat_lang


def gen_langs_kb():
    return [
        [
            InlineKeyboardButton(
                f"{langdict[lang]['main']['language_flag']} {langdict[lang]['main']['language_name']}",
                callback_data=f"set_lang {lang}",
            )
            for lang in langs
            if lang
        ]
        for langs in zip_longest(*[iter(langdict)] * 2)
    ]


@Client.on_callback_query(filters.regex("^chlang$"))
@Client.on_message(filters.command(["setchatlang", "setlang"], PREFIXES) & filters.group)
@require_admin(allow_in_private=True)
@use_chat_lang
async def chlang(c: Client, m: Union[CallbackQuery, Message], strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *gen_langs_kb(),
            [
                InlineKeyboardButton(
                    strings("back_btn", context="general"), callback_data="start_back"
                )
            ],
        ]
    )

    if isinstance(m, CallbackQuery):
        msg = m.message
        sender = msg.edit_text
    else:
        msg = m
        sender = msg.reply_text

    res = (
        strings("language_changer_private")
        if msg.chat.type == ChatType.PRIVATE
        else strings("language_changer_chat")
    )

    await sender(res, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^set_lang "))
@require_admin(allow_in_private=True)
async def set_chat_lang(c: Client, m: CallbackQuery):
    lang = m.data.split()[1]
    await set_db_lang(m.message.chat.id, m.message.chat.type, lang)

    await set_chat_lang_edit(c, m)


@use_chat_lang
async def set_chat_lang_edit(c: Client, m: CallbackQuery, strings):
    if m.message.chat.type == ChatType.PRIVATE:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        strings("back_btn", context="general"),
                        callback_data="start_back",
                    )
                ]
            ]
        )
    else:
        keyboard = None
    await m.message.edit_text(strings("language_changed_successfully"), reply_markup=keyboard)
