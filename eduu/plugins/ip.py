# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from yarl import URL

from config import PREFIXES

from ..utils import http
from ..utils.localization import use_chat_lang


async def get_ip_info(ip: str) -> str:
    r = await http.get(f"http://ip-api.com/json/{ip}")
    req = r.json()
    return "\n".join(f"<b>{i.title()}</b>: <code>{req[i]}</code>" for i in req)


@Client.on_message(filters.command("ip", PREFIXES))
@use_chat_lang()
async def ip_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        text = m.text.split(maxsplit=1)[1]
        url: str = URL(text).host or text

        await m.reply_text(await get_ip_info(url))
    else:
        await m.reply_text(strings("ip_err_no_ip"))


@Client.on_inline_query(filters.regex(r"^ip"))
@use_chat_lang()
async def ip_inline(c: Client, q: InlineQuery, strings):
    if len(q.query.split()) > 1:
        text = q.query.split(maxsplit=1)[1]
        url: str = URL(text).host or text

        await q.answer(
            [
                InlineQueryResultArticle(
                    title=strings("ip_info_inline").format(domain=url),
                    input_message_content=InputTextMessageContent(
                        await get_ip_info(url)
                    ),
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
