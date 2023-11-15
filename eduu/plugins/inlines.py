# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import re
from typing import Iterable, List

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import PeerIdInvalid, UserIdInvalid, UsernameInvalid
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from eduu.utils import button_parser, inline_commands
from eduu.utils.localization import use_chat_lang

faces_list: Iterable[str] = (
    "¯\\_(ツ)_/¯",
    "( ͡° ͜ʖ ͡°)",
    "( ͡~ ͜ʖ ͡°)",
    "( ͡◐ ͜ʖ ͡◑))",
    "( ͡◔ ͜ʖ ͡◔)",
    "( ͡⚆ ͜ʖ ͡⚆)",
    "( ͡ʘ ͜ʖ ͡ʘ)",
    "ヽ༼ຈل͜ຈ༽ﾉ",
    "༼ʘ̚ل͜ʘ̚༽",
    "(╯°□°）╯",
    "(ﾉ◕ヮ◕)ﾉ",
    "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
    "(◕‿◕)",
    "(｡◕‿‿◕｡)",
    "(っ◕‿◕)っ",
    "(づ｡◕‿‿◕｡)づ",
    "༼ つ ◕_◕ ༽つ",
    "(ง ͠° ͟ل͜ ͡°)ง",
    "(ง'̀-'́)ง",
    "ᕙ(⇀‸↼‶)ᕗ",
    "(҂⌣̀_⌣́)",
    "ᕦ(ò_óˇ)ᕤ",
    "╚(ಠ_ಠ)=┐",
    "ლ(ಠ益ಠლ)",
    "\\_(ʘ_ʘ)_/",
    "( ⚆ _ ⚆ )",
    "(ಥ﹏ಥ)",
    "﴾͡๏̯͡๏﴿",
    "(◔̯◔)",
    "(ಠ_ಠ)",
    "(ಠ‿ಠ)",
    "(¬_¬)",
    "(¬‿¬)",
    "\\ (•◡•) /",
    "(◕‿◕✿)",
    "( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)",
)


@Client.on_inline_query(filters.regex(r"^face", re.I))
async def faces_inline(c: Client, q: InlineQuery):
    results: List[InlineQueryResultArticle] = [
        InlineQueryResultArticle(title=i, input_message_content=InputTextMessageContent(i))
        for i in faces_list
    ]

    await q.answer(results)


@Client.on_inline_query(filters.regex(r"^markdown .+", re.I))
@use_chat_lang
async def markdown_inline(c: Client, q: InlineQuery, strings):
    queryinputres = q.query.split(None, 1)[1]
    querytxt, querybuttons = button_parser(queryinputres)
    await q.answer(
        [
            InlineQueryResultArticle(
                title=strings("markdown_send_inline"),
                input_message_content=InputTextMessageContent(
                    querytxt, parse_mode=ParseMode.MARKDOWN
                ),
                reply_markup=(
                    InlineKeyboardMarkup(querybuttons) if len(querybuttons) != 0 else None
                ),
            )
        ]
    )


@Client.on_inline_query(filters.regex(r"^html .+", re.I))
@use_chat_lang
async def html_inline(c: Client, q: InlineQuery, strings):
    queryinputres = q.query.split(None, 1)[1]
    querytxt, querybuttons = button_parser(queryinputres)
    await q.answer(
        [
            InlineQueryResultArticle(
                title=strings("html_send_inline"),
                input_message_content=InputTextMessageContent(
                    querytxt,
                ),
                reply_markup=(
                    InlineKeyboardMarkup(querybuttons) if len(querybuttons) != 0 else None
                ),
            )
        ]
    )


@Client.on_inline_query(filters.regex(r"^info .+", re.I))
@use_chat_lang
async def info_inline(c: Client, q: InlineQuery, strings):
    try:
        if q.query == "info":
            user = q.from_user
        elif q.query.lower().split(None, 1)[1]:
            txt = q.query.lower().split(None, 1)[1]
            user = await c.get_users(txt)
    except (PeerIdInvalid, UsernameInvalid, UserIdInvalid):
        return await q.answer(
            [
                InlineQueryResultArticle(
                    title=strings("user_info_inline_cant_found_user"),
                    input_message_content=InputTextMessageContent(
                        strings("user_info_inline_cant_found_user")
                    ),
                )
            ]
        )
    await q.answer(
        [
            InlineQueryResultArticle(
                title=strings("user_info_inline_send"),
                input_message_content=InputTextMessageContent(
                    strings("user_info_inline_string").format(
                        usernameformat=user.username,
                        useridformat=user.id,
                        userdcformat=user.dc_id,
                        usermentionformat=user.mention(),
                    ),
                ),
            )
        ]
    )
    return None


inline_commands.add_command("faces")
inline_commands.add_command("html <text>")
inline_commands.add_command("info <username>")
inline_commands.add_command("markdown <text>")
