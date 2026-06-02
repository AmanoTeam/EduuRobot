# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2026 Amano LLC

import re
from collections.abc import Iterable

from hydrogram import Client, filters
from hydrogram.enums import ParseMode
from hydrogram.errors import PeerIdInvalid, UserIdInvalid, UsernameInvalid
from hydrogram.types import (
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from eduu.utils import button_parser, inline_commands
from eduu.utils.localization import Strings, use_chat_lang

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


@Client.on_inline_query(filters.regex(r"^face", re.IGNORECASE))
async def faces_inline(c: Client, q: InlineQuery):
    results: list[InlineQueryResultArticle] = [
        InlineQueryResultArticle(title=i, input_message_content=InputTextMessageContent(i))
        for i in faces_list
    ]

    await q.answer(results)


@Client.on_inline_query(filters.regex(r"^markdown .+", re.IGNORECASE))
@use_chat_lang
async def markdown_inline(c: Client, q: InlineQuery, s: Strings):
    queryinputres = q.query.split(None, 1)[1]
    querytxt, querybuttons = button_parser(queryinputres)
    await q.answer([
        InlineQueryResultArticle(
            title=s("markdown_send_inline"),
            input_message_content=InputTextMessageContent(querytxt, parse_mode=ParseMode.MARKDOWN),
            reply_markup=(InlineKeyboardMarkup(querybuttons) if len(querybuttons) != 0 else None),
        )
    ])


@Client.on_inline_query(filters.regex(r"^html .+", re.IGNORECASE))
@use_chat_lang
async def html_inline(c: Client, q: InlineQuery, s: Strings):
    queryinputres = q.query.split(None, 1)[1]
    querytxt, querybuttons = button_parser(queryinputres)
    await q.answer([
        InlineQueryResultArticle(
            title=s("html_send_inline"),
            input_message_content=InputTextMessageContent(
                querytxt,
            ),
            reply_markup=(InlineKeyboardMarkup(querybuttons) if len(querybuttons) != 0 else None),
        )
    ])


@Client.on_inline_query(filters.regex(r"^info .+", re.IGNORECASE))
@use_chat_lang
async def info_inline(c: Client, q: InlineQuery, s: Strings):
    try:
        if q.query == "info":
            user = q.from_user
        elif q.query.lower().split(None, 1)[1]:
            txt = q.query.lower().split(None, 1)[1]
            user = await c.get_users(txt)
    except (PeerIdInvalid, UsernameInvalid, UserIdInvalid):
        await q.answer([
            InlineQueryResultArticle(
                title=s("user_info_inline_couldnt_find_user"),
                input_message_content=InputTextMessageContent(
                    s("user_info_inline_couldnt_find_user")
                ),
            )
        ])
        return
    await q.answer([
        InlineQueryResultArticle(
            title=s("user_info_inline_send"),
            input_message_content=InputTextMessageContent(
                s("user_info_inline_string").format(
                    username=user.username,
                    user_id=user.id,
                    user_dc=user.dc_id,
                    user_mention=user.mention(),
                ),
            ),
        )
    ])


inline_commands.add_command("faces")
inline_commands.add_command("html <text>")
inline_commands.add_command("info <username>")
inline_commands.add_command("markdown <text>")
