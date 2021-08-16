# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import html

import regex
from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.utils.localization import use_chat_lang
from eduu.utils.bot_error_log import logging_errors


@Client.on_message(filters.regex(r"^s/(.+)?/(.+)?(/.+)?") & filters.reply)
@use_chat_lang()
@logging_errors
async def sed(c: Client, m: Message, strings):
    exp = regex.split(r"(?<![^\\]\\)/", m.text)
    pattern = exp[1]
    replace_with = exp[2].replace(r"\/", "/")
    flags = exp[3] if len(exp) > 3 else ""

    count = 1
    rflags = 0

    if "g" in flags:
        count = 0
    if "i" in flags and "s" in flags:
        rflags = regex.I | regex.S
    elif "i" in flags:
        rflags = regex.I
    elif "s" in flags:
        rflags = regex.S

    text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        return

    try:
        res = regex.sub(
            pattern, replace_with, text, count=count, flags=rflags, timeout=1
        )
    except TimeoutError:
        await m.reply_text(strings("regex_timeout"))
    except regex.error as e:
        await m.reply_text(str(e))
    else:
        await c.send_message(
            m.chat.id,
            f"<pre>{html.escape(res)}</pre>",
            reply_to_message_id=m.reply_to_message.message_id,
        )
