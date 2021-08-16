from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from eduu.config import nekobin_error_paste_url, log_chat
from eduu.utils.consts import http
from functools import wraps
import traceback, html


def logging_errors(f):
    @wraps(f)
    async def err_log(c: Client, m: Message, *args, **kwargs):
        try:
            return await f(c, m, *args, **kwargs)
        except ChatWriteForbidden:
            return await m.chat.leave()
        except Exception as e:
            if c.log_chat_errors:
                full_trace = traceback.format_exc()
                try:
                    paste_err = await http.post(
                        f"{nekobin_error_paste_url}/api/documents",
                        json={"content": full_trace},
                    )
                    pastereqjson = paste_err.json()["result"]
                    paste_url = f"{nekobin_error_paste_url}/{pastereqjson['key']}"
                    thefulltrace = f"the full trace: {paste_url}"
                except:
                    thefulltrace = "error has occurred in the paste"
                try:
                    await c.send_message(
                        log_chat,
                        f"Error message\n\n<code>{type(e).__name__}: {html.escape(str(e))}</code>\n\n{thefulltrace}",
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Delete this message",
                                        callback_data="delete_error_message_callback",
                                    )
                                ],
                            ]
                        ),
                    )
                except Exception as e:
                    pass

    return err_log
