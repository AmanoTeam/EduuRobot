from pytio import Tio, TioRequest
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from config import prefix

tio = Tio()

def getlangs():
    langs = tio.query_languages()
    return langs


@Client.on_message(filters.command("exec_code", prefix))
async def exec_tio_run_code(c: Client, m: Message):
    execlanguage = m.command[1]
    langslist = getlangs()
    codetoexec = m.text.split(None, 2)[2]
    if execlanguage in langslist:
        tioreq = TioRequest(lang=execlanguage, code=codetoexec)
        sendtioreq = tio.send(tioreq)
        await m.reply_text(
            f"language:\n\n<code>{execlanguage}</code>\n\ncode:\n\n<code>{codetoexec}</code>\n\nresults:\n\n<code>{sendtioreq.result}</code>\n\n errors:\n\n<code>{sendtioreq.error}</code>"
        )
    else:
        await m.reply_text(
            f"error: the language {execlanguage} not found, the supported languages list: https://nekobin.com/tavijipafa"
        )


@Client.on_inline_query(filters.regex(r"^exec"))
async def exec_tio_run_code_inline(c: Client, q: InlineQuery):
    codetoexec = q.query.split(None, 2)[2]
    execlanguage = q.query.lower().split()[1]
    langslist = getlangs()
    if execlanguage in langslist:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=f"language:\n\n<code>{execlanguage}</code>\n\ncode:\n\n<code>{codetoexec}</code>\n\nresults:\n\n<code>{sendtioreq.result}</code>\n\n errors:\n\n<code>{sendtioreq.error}</code>",
                    input_message_content=InputTextMessageContent(
                        f"language:\n\n<code>{execlanguage}</code>\n\ncode:\n\n<code>{codetoexec}</code>\n\nresults:\n\n<code>{sendtioreq.result}</code>\n\n errors:\n\n<code>{sendtioreq.error}</code>"
                    ),
                )
            ]
        )
    else:
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=f"error: the language {execlanguage} not found, the supported languages list: https://nekobin.com/tavijipafa",
                    input_message_content=InputTextMessageContent(
                        f"error: the language {execlanguage} not found, the supported languages list: https://nekobin.com/tavijipafa"
                    ),
                )
            ]
        )
