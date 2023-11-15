# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from itertools import zip_longest

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from eduu.utils import commands
from eduu.utils.decorators import stop_here
from eduu.utils.localization import use_chat_lang


def gen_categories_kb(strings_manager):
    return [
        [
            InlineKeyboardButton(
                strings_manager(category, context="cmds_list"),
                callback_data=f"view_category {category}",
            )
            for category in categories
            if category
        ]
        for categories in zip_longest(*[iter(commands.commands)] * 2)
    ]


@Client.on_callback_query(filters.regex("^commands$"))
@use_chat_lang
async def cmds_list(c: Client, m: CallbackQuery, strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *gen_categories_kb(strings),
            [
                InlineKeyboardButton(
                    strings("back_btn", context="general"), callback_data="start_back"
                )
            ],
        ]
    )
    await m.message.edit_text(strings("select_command_category"), reply_markup=keyboard)


@Client.on_message(filters.command(["help", "start help"]) & filters.private)
@use_chat_lang
@stop_here
async def show_private_help(c: Client, m: Message, strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *gen_categories_kb(strings),
            [
                InlineKeyboardButton(
                    strings("back_btn", context="general"),
                    callback_data="start_back",
                )
            ],
        ]
    )
    await m.reply_text(strings("select_command_category"), reply_markup=keyboard)


@Client.on_message(filters.command(["help", "start help"]))
@use_chat_lang
@stop_here
async def show_help(c: Client, m: Message, strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    strings("start_chat", context="start"),
                    url=f"https://t.me/{c.me.username}?start=help",
                )
            ]
        ]
    )
    await m.reply_text(strings("group_help"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^view_category .+"))
@use_chat_lang
async def get_category(c: Client, m: CallbackQuery, strings):
    msg = commands.get_commands_message(strings, m.data.split(maxsplit=1)[1])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    strings("back_btn", context="general"), callback_data="commands"
                )
            ]
        ]
    )
    await m.message.edit_text(msg, reply_markup=keyboard)
