# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from typing import Union

from hydrogram import Client, filters
from hydrogram.types import (
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
@Client.on_message(filters.command("start", PREFIXES) & filters.private, group=2)
@Client.on_callback_query(filters.regex("^start_back$"))
@use_chat_lang
async def start_pvt(c: Client, m: Union[Message, CallbackQuery], strings):
    if isinstance(m, CallbackQuery):
        msg = m.message
        send = msg.edit_text
    else:
        msg = m
        send = msg.reply_text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(strings("commands_btn"), callback_data="commands"),
                InlineKeyboardButton(strings("infos_btn"), callback_data="infos"),
            ],
            [
                InlineKeyboardButton(strings("language_btn"), callback_data="chlang"),
                InlineKeyboardButton(
                    strings("add_chat_btn"),
                    url=f"https://t.me/{c.me.username}?startgroup=new",
                ),
            ],
        ]
    )
    await send(strings("private"), reply_markup=keyboard)


@Client.on_message(filters.command("start", PREFIXES) & filters.group, group=2)
@use_chat_lang
async def start_grp(c: Client, m: Union[Message, CallbackQuery], strings):
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
    await m.reply_text(strings("group"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^infos$"))
@use_chat_lang
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
