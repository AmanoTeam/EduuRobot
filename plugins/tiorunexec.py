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

def getlangs():
    langs = tio.query_languages()
    return langs


@Client.on_message(filters.command("exec_code", prefix))
@use_chat_lang()
async def exec_tio_run_code(c: Client, m: Message, strings):
    execlanguage = m.command[1]
    langslist = getlangs()
    codetoexec = m.text.split(None, 2)[2]
    if execlanguage in langslist:
        tioreq = TioRequest(lang=execlanguage, code=codetoexec)
        sendtioreq = tio.send(tioreq)
        await m.reply_text(strings("code_exec_tio_res_string").format(langformat=execlanguage, codeformat=codetoexec, resformat=sendtioreq.result, errformat=sendtioreq.error))
    else:
        await m.reply_text(strings("code_exec_err_string").format(langformat=execlanguage))


@Client.on_inline_query(filters.regex(r"^exec"))
async def exec_tio_run_code_inline(c: Client, q: InlineQuery):
    codetoexec = q.query.split(None, 2)[2]
    execlanguage = q.query.lower().split()[1]
    langslist = getlangs()
    if execlanguage in langslist:
        tioreq = TioRequest(lang=execlanguage, code=codetoexec)
        sendtioreq = tio.send(tioreq)
        await q.answer(
            [
                InlineQueryResultArticle(
                    title=f"language: {execlanguage} code:  {codetoexec}",
                    input_message_content=InputTextMessageContent(
                        f"<b>language:</b>\n\n<code>{execlanguage}</code>\n\n<b>code:</b>\n\n<code>{codetoexec}</code>\n\n<b>results:</b>\n\n<code>{sendtioreq.result}</code>\n\n<b>errors:</b>\n\n<code>{sendtioreq.error}</code>"
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
