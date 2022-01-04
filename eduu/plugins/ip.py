# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from yarl import URL

from eduu.config import prefix
from eduu.utils import http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("ip", prefix))
@use_chat_lang()
async def ip_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        text = m.text.split(maxsplit=1)[1]
        url: str = URL(text).host or text

        r = await http.get("http://ip-api.com/json/" + url)
        req = r.json()
        x = ""
        for i in req:
            x += "<b>{}</b>: <code>{}</code>\n".format(i.title(), req[i])
        await m.reply_text(x)
    else:
        await m.reply_text(strings("ip_err_no_ip"))


@Client.on_inline_query(filters.regex(r"^ip"))
@use_chat_lang()
async def ip_inline(c: Client, q: InlineQuery, strings):
    if len(q.query.split()) > 1:
        text = q.query.split(maxsplit=1)[1]
        url: str = URL(text).host or text

        r = await http.get("http://ip-api.com/json/" + url)
        req = r.json()
        x = ""
        for i in req:
            x += "<b>{}</b>: <code>{}</code>\n".format(i.title(), req[i])
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=strings("ip_info_inline").format(domain=url),
                    input_message_content=InputTextMessageContent(x),
                )
            ]
        )
    else:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=strings("ip_no_url"),
                    input_message_content=InputTextMessageContent(
                        strings("ip_no_url_example").format(bot_username=c.me.username),
                    ),
                )
            ]
        )
