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
langs_list_link = "https://amanoteam.com/langs/"


def normalize_language_name(language_name: str) -> str:
    """
    Used for transforming user-provided language name into valid choices.
    """
    if language_name == "python":
        return "python3"
    if language_name == "c":
        return "c-clang"
    if language_name in {"cpp", "cxx", "c++"}:
        return "cpp-clang"
    if language_name in {"javascript", "js"}:
        return "javascript-node"
    if language_name == "java":
        return "java-openjdk"
    if language_name in {"c#", "cs"}:
        return "cs-core"
    return language_name


def pre_normalize_language_name(language_name: str) -> str:
    """
    Used for transforming language name into code highlight language name.
    """
    if language_name.startswith("python"):
        return "python"
    if language_name.startswith("perl"):
        return "perl"
    if language_name.startswith("lua"):
        return "lua"
    if language_name.startswith("assembly-"):
        return "asm"
    if language_name.startswith("haskell-"):
        return "haskell"
    if language_name.startswith("java-"):
        return "java"
    if language_name.startswith("javascript-"):
        return "javascript"
    if language_name.startswith("c-"):
        return "c"
    if language_name.startswith("cpp-"):
        return "cpp"
    if language_name.startswith("objective-c-"):
        return "objective-c"
    if language_name.startswith("cs-"):
        return "cs"

    # return the language itself
    return language_name


@Client.on_message(filters.command(["run", "exec_code"], PREFIXES))
@use_chat_lang
async def exec_tio_run_code(c: Client, m: Message, s: Strings):
    requested_language = normalize_language_name(m.command[1].lower())
    pre_language = pre_normalize_language_name(requested_language)
    if requested_language not in langslist:
        await m.reply_text(
            s("run_err_string").format(
                language=requested_language, supported_langs=langs_list_link
            )
        )
        return

    codetoexec = m.text.split(None, 2)[2]
    tioreq = TioRequest(lang=requested_language, code=codetoexec)
    loop = asyncio.get_event_loop()
    sendtioreq = await loop.run_in_executor(None, tio.send, tioreq)
    tioerrres = sendtioreq.error or "None"
    tiores = sendtioreq.result or "None"
    tioresstats = sendtioreq.debug.decode() or "None"

    if sendtioreq.error is None:
        await m.reply_text(
            s("run_tio_res_string_no_err").format(
                language=requested_language,
                pre_language=pre_language,
                code=html.escape(codetoexec),
                results=html.escape(tiores),
                stats=tioresstats,
            )
        )
        return

    await m.reply_text(
        s("run_tio_res_string_err").format(
            language=requested_language,
            pre_language=pre_language,
            code=html.escape(codetoexec),
            results=html.escape(tiores),
            errors=html.escape(tioerrres),
        )
    )


@Client.on_inline_query(filters.regex(r"^(run|exec)", re.IGNORECASE))
@use_chat_lang
async def exec_tio_run_code_inline(c: Client, q: InlineQuery, s: Strings):
    requested_language = normalize_language_name(q.query.lower().split()[1])
    pre_language = pre_normalize_language_name(requested_language)
    if requested_language not in langslist:
        await q.answer([
            InlineQueryResultArticle(
                title=s("run_err_inline_send_string").format(language=requested_language),
                input_message_content=InputTextMessageContent(
                    s("run_err_string").format(
                        language=requested_language, supported_langs=langs_list_link
                    )
                ),
            )
        ])
        return

    codetoexec = q.query.split(None, 2)[2]
    tioreq = TioRequest(lang=requested_language, code=codetoexec)
    loop = asyncio.get_event_loop()
    sendtioreq = await loop.run_in_executor(None, tio.send, tioreq)
    tioerrres = sendtioreq.error or "None"
    tiores = sendtioreq.result or "None"
    tioresstats = sendtioreq.debug.decode() or "None"

    if sendtioreq.error is None:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=s("run_inline_send").format(language=requested_language),
                    description=tiores,
                    input_message_content=InputTextMessageContent(
                        s("run_tio_res_string_no_err").format(
                            language=requested_language,
                            pre_language=pre_language,
                            code=html.escape(codetoexec),
                            results=html.escape(tiores),
                            stats=tioresstats,
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
                title=s("run_inline_send").format(language=requested_language),
                description=tiores,
                input_message_content=InputTextMessageContent(
                    s("run_tio_res_string_err").format(
                        language=requested_language,
                        pre_language=pre_language,
                        code=html.escape(codetoexec),
                        results=html.escape(tiores),
                        errors=html.escape(tioerrres),
                    )
                ),
            )
        ],
        cache_time=0,
    )


commands.add_command("run", "tools")
inline_commands.add_command("run <lang> <code>", aliases=["exec"])
