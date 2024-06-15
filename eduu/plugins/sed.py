# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import html

import regex
from hydrogram import Client, filters
from hydrogram.types import Message

from eduu.utils.localization import Strings, use_chat_lang


@Client.on_message(filters.regex(r"^s/(.+)?/(.+)?(/.+)?") & filters.reply)
@use_chat_lang
async def sed(c: Client, m: Message, s: Strings):
    exp = regex.split(r"(?<![^\\]\\)/", m.text)
    pattern = exp[1]
    replace_with = exp[2].replace(r"\/", "/")
    flags = exp[3] if len(exp) > 3 else ""

    rflags = 0

    count = 0 if "g" in flags else 1
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
        res = regex.sub(pattern, replace_with, text, count=count, flags=rflags, timeout=1)
    except TimeoutError:
        await m.reply_text(s("sed_regex_timeout"))
    except regex.error as e:
        await m.reply_text(str(e))
    else:
        await c.send_message(
            m.chat.id,
            f"<pre>{html.escape(res)}</pre>",
            reply_to_message_id=m.reply_to_message.id,
        )
