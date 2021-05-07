import asyncio
import html

from config import prefix
from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from pytio import Tio, TioRequest

from localization import use_chat_lang

tio = Tio()


langslist = tio.query_languages()


@Client.on_message(filters.command("exec_code", prefix))
@use_chat_lang()
async def exec_tio_run_code(c: Client, m: Message, strings):
    execlanguage = m.command[1]
    codetoexec = m.text.split(None, 2)[2]
    if execlanguage in langslist:
        tioreq = TioRequest(lang=execlanguage, code=codetoexec)
        loop = asyncio.get_event_loop()
        sendtioreq = await loop.run_in_executor(None, tio.send, tioreq)
        tioerrres = sendtioreq.error or "None"
        tiores = sendtioreq.result or "None"
        tioresstats = sendtioreq.debug.decode() or "None"
        if sendtioreq.error is None:
            await m.reply_text(
                strings("code_exec_tio_res_string_no_err").format(
                    langformat=execlanguage,
                    codeformat=html.escape(codetoexec),
                    resformat=html.escape(tiores),
                    statsformat=tioresstats,
                )
            )
        else:
            await m.reply_text(
                strings("code_exec_tio_res_string_err").format(
                    langformat=execlanguage,
                    codeformat=html.escape(codetoexec),
                    resformat=html.escape(tiores),
                    errformat=html.escape(tioerrres),
                )
            )
    else:
        await m.reply_text(
            strings("code_exec_err_string").format(langformat=execlanguage)
        )


@Client.on_inline_query(filters.regex(r"^exec"))
@use_chat_lang()
async def exec_tio_run_code_inline(c: Client, q: InlineQuery, strings):
    codetoexec = q.query.split(None, 2)[2]
    execlanguage = q.query.lower().split()[1]
    if execlanguage in langslist:
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
                        title=strings("code_exec_inline_send").format(
                            langformat=execlanguage, codeformat=codetoexec
                        ),
                        input_message_content=InputTextMessageContent(
                            strings("code_exec_tio_res_string_no_err").format(
                                langformat=execlanguage,
                                codeformat=html.escape(codetoexec),
                                resformat=html.escape(tiores),
                                statsformat=tioresstats,
                            )
                        ),
                    )
                ]
            )
        else:
            await q.answer(
                [
                    InlineQueryResultArticle(
                        title=strings("code_exec_inline_send").format(
                            langformat=execlanguage, codeformat=codetoexec
                        ),
                        input_message_content=InputTextMessageContent(
                            strings("code_exec_tio_res_string_err").format(
                                langformat=execlanguage,
                                codeformat=html.escape(codetoexec),
                                resformat=html.escape(tiores),
                                errformat=html.escape(tioerrres),
                            )
                        ),
                    )
                ]
            )
    else:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=strings("code_exec_err_inline_send_string").format(
                        langformat=execlanguage
                    ),
                    input_message_content=InputTextMessageContent(
                        strings("code_exec_err_string").format(langformat=execlanguage)
                    ),
                )
            ]
        )
