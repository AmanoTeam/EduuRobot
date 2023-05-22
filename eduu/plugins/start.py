# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

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
from eduu import __commit__, __version_number__
from eduu.utils import commands, linkify_commit
from eduu.utils.localization import use_chat_lang


# Using a low priority group so deeplinks will run before this and stop the propagation.
@Client.on_message(filters.command("start", PREFIXES), group=2)
@Client.on_callback_query(filters.regex("^start_back$"))
@use_chat_lang()
async def start(c: Client, m: Union[Message, CallbackQuery], strings):
    if isinstance(m, CallbackQuery):
        msg = m.message
        method = msg.edit_text
    else:
        msg = m
        method = msg.reply_text

    if msg.chat.type == ChatType.PRIVATE:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        strings("commands_btn"), callback_data="commands"
                    ),
                    InlineKeyboardButton(strings("infos_btn"), callback_data="infos"),
                ],
                [
                    InlineKeyboardButton(
                        strings("language_btn"), callback_data="chlang"
                    ),
                    InlineKeyboardButton(
                        strings("add_chat_btn"),
                        url=f"https://t.me/{c.me.username}?startgroup=new",
                    ),
                ],
            ]
        )
        await method(strings("private"), reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        strings("start_chat"),
                        url=f"https://t.me/{c.me.username}?start=start",
                    )
                ]
            ]
        )
        await method(strings("group"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^infos$"))
@use_chat_lang()
async def infos(c: Client, m: CallbackQuery, strings):
    res = strings("info_page").format(
        version_number=f"r{__version_number__}",
        commit_hash=linkify_commit(__commit__),
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    strings("back_btn", context="general"), callback_data="start_back"
                )
            ]
        ]
    )
    await m.message.edit_text(res, reply_markup=keyboard, disable_web_page_preview=True)


commands.add_command("start", "general")
