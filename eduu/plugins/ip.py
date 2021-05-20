# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import re

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from eduu.config import prefix
from eduu.utils.consts import http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("ip", prefix))
@use_chat_lang()
async def ip_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        text = m.text.split(maxsplit=1)[1]
        if text.startswith("http"):
            url = re.sub("http(s|)://", "", text)
        else:
            url = text
        r = await http.get("http://ip-api.com/json/" + url)
        req = r.json()
        x = ""
        for i in req:
            x += "<b>{}</b>: <code>{}</code>\n".format(i.title(), req[i])
        await m.reply_text(x, parse_mode="html")
    else:
        await m.reply_text(strings("ip_err_no_ip"))


@Client.on_inline_query(filters.regex(r"^ip"))
async def ip_inline(c: Client, q: InlineQuery):
    getme = await c.get_me()
    if len(q.query.split()) > 1:
        text = q.query.split(maxsplit=1)[1]
        if text.startswith("http"):
            url = re.sub("http(s|)://", "", text)
        else:
            url = text
        r = await http.get("http://ip-api.com/json/" + url)
        req = r.json()
        x = ""
        for i in req:
            x += "<b>{}</b>: <code>{}</code>\n".format(i.title(), req[i])
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=f"click here to see the ip of {text}",
                    input_message_content=InputTextMessageContent(x, parse_mode="html"),
                )
            ]
        )
    else:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title="You must specify the url",
                    input_message_content=InputTextMessageContent(
                        f"You must specify the url, E.g.: <code>@{getme.username} ip example.com</code>",
                        parse_mode="html",
                    ),
                )
            ]
        )
