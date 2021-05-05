import asyncio, html
from pytio import Tio, TioRequest
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from config import prefix
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
        tioexeccodestats = sendtioreq.debug.decode()
        if sendtioreq.error is None:
            await m.reply_text(
                strings("code_exec_tio_res_string_no_err").format(
                    langformat=execlanguage,
                    codeformat=codetoexec,
                    resformat=sendtioreq.result,
                    statsformat=tioexeccodestats,
                )
            )
        else:
            await m.reply_text(
                strings("code_exec_tio_res_string_err").format(
                    langformat=execlanguage,
                    codeformat=codetoexec,
                    resformat=sendtioreq.result,
                    errformat=sendtioreq.error,
                )
            )
    else:
        await m.reply_text(
            strings("code_exec_err_string").format(langformat=execlanguage)
        )


@Client.on_inline_query(filters.regex(r"^exec"))
async def exec_tio_run_code_inline(c: Client, q: InlineQuery):
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
                        title=f"Language: {execlanguage} - Code:  {codetoexec}",
                        input_message_content=InputTextMessageContent(
                            f"<b>Language:</b>\n\n<code>{execlanguage}</code>\n\n<b>Code:</b>\n\n<code>{html.escape(codetoexec)}</code>\n\n<b>Results:</b>\n\n<code>{html.escape(tiores)}</code>\n\n<b>Stats:</b>\n\n<code>{tioresstats}</code>"
                        ),
                    )
                ]
            )
        else:
            await q.answer(
                [
                    InlineQueryResultArticle(
                        title=f"Language: {execlanguage} - Code:  {codetoexec}",
                        input_message_content=InputTextMessageContent(
                            f"<b>Language:</b>\n\n<code>{execlanguage}</code>\n\n<b>Code:</b>\n\n<code>{html.escape(codetoexec)}</code>\n\n<b>Results:</b>\n\n<code>{html.escape(tiores)}</code>\n\n<b>Errors:</b>\n\n<code>{html.escape(tioerrres)}</code>"
                        ),
                    )
                ]
            )
    else:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=f"Language {execlanguage} not found.",
                    input_message_content=InputTextMessageContent(
                        f"Error: The language {execlanguage} was not found. Supported languages list: https://nekobin.com/tavijipafa"
                    ),
                )
            ]
        )
