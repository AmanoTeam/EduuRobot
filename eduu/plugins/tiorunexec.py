# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import asyncio
import html
import re

from hydrogram import Client, filters
from hydrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from pytio import Tio, TioRequest

from config import PREFIXES
from eduu.utils import commands, inline_commands
from eduu.utils.localization import Strings, use_chat_lang

tio = Tio()


langslist = tio.query_languages()
langs_list_link = "https://amanoteam.com/etc/langs.html"


@Client.on_message(filters.command(["run", "exec_code"], PREFIXES))
@use_chat_lang
async def exec_tio_run_code(c: Client, m: Message, s: Strings):
    execlanguage = m.command[1]
    if execlanguage not in langslist:
        await m.reply_text(
            s("run_err_string").format(langformat=execlanguage, langslistlink=langs_list_link)
        )
        return

    codetoexec = m.text.split(None, 2)[2]
    tioreq = TioRequest(lang=execlanguage, code=codetoexec)
    loop = asyncio.get_event_loop()
    sendtioreq = await loop.run_in_executor(None, tio.send, tioreq)
    tioerrres = sendtioreq.error or "None"
    tiores = sendtioreq.result or "None"
    tioresstats = sendtioreq.debug.decode() or "None"

    if sendtioreq.error is None:
        await m.reply_text(
            s("run_tio_res_string_no_err").format(
                langformat=execlanguage,
                codeformat=html.escape(codetoexec),
                resformat=html.escape(tiores),
                statsformat=tioresstats,
            )
        )
        return

    await m.reply_text(
        s("run_tio_res_string_err").format(
            langformat=execlanguage,
            codeformat=html.escape(codetoexec),
            resformat=html.escape(tiores),
            errformat=html.escape(tioerrres),
        )
    )


@Client.on_inline_query(filters.regex(r"^(run|exec)", re.IGNORECASE))
@use_chat_lang
async def exec_tio_run_code_inline(c: Client, q: InlineQuery, s: Strings):
    execlanguage = q.query.lower().split()[1]
    if execlanguage not in langslist:
        await q.answer([
            InlineQueryResultArticle(
                title=s("run_err_inline_send_string").format(langformat=execlanguage),
                input_message_content=InputTextMessageContent(
                    s("run_err_string").format(
                        langformat=execlanguage, langslistlink=langs_list_link
                    )
                ),
            )
        ])
        return

    codetoexec = q.query.split(None, 2)[2]
    tioreq = TioRequest(lang=execlanguage, code=codetoexec)
    loop = asyncio.get_event_loop()
    sendtioreq = await loop.run_in_executor(None, tio.send, tioreq)
    tioerrres = sendtioreq.error or "None"
    tiores = sendtioreq.result or "None"
    tioresstats = sendtioreq.debug.decode() or "None"

    if sendtioreq.error is None:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=s("run_inline_send").format(langformat=execlanguage),
                    description=tiores,
                    input_message_content=InputTextMessageContent(
                        s("run_tio_res_string_no_err").format(
                            langformat=execlanguage,
                            codeformat=html.escape(codetoexec),
                            resformat=html.escape(tiores),
                            statsformat=tioresstats,
                        )
                    ),
                )
            ],
            cache_time=0,
        )
        return

    await q.answer(
        [
            InlineQueryResultArticle(
                title=s("run_inline_send").format(langformat=execlanguage),
                description=tiores,
                input_message_content=InputTextMessageContent(
                    s("run_tio_res_string_err").format(
                        langformat=execlanguage,
                        codeformat=html.escape(codetoexec),
                        resformat=html.escape(tiores),
                        errformat=html.escape(tioerrres),
                    )
                ),
            )
        ],
        cache_time=0,
    )


commands.add_command("run", "tools")
inline_commands.add_command("run <lang> <code>", aliases=["exec"])
