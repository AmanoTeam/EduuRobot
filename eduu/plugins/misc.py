# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import re
from html import escape
from urllib.parse import quote, unquote

from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import InlineKeyboardMarkup, Message

from eduu.config import log_chat, prefix
from eduu.utils import button_parser, commands
from eduu.utils.consts import admin_status, http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("mark", prefix))
@use_chat_lang()
async def mark(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("mark_usage"))
    txt = m.text.split(None, 1)[1]
    msgtxt, buttons = button_parser(txt)
    await m.reply(
        msgtxt,
        parse_mode="markdown",
        reply_markup=(InlineKeyboardMarkup(buttons) if len(buttons) != 0 else None),
    )


@Client.on_message(filters.command("html", prefix))
@use_chat_lang()
async def html(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("html_usage"))
    txt = m.text.split(None, 1)[1]
    msgtxt, buttons = button_parser(txt)
    await m.reply(
        msgtxt,
        reply_markup=(InlineKeyboardMarkup(buttons) if len(buttons) != 0 else None),
    )


@Client.on_message(filters.command("admins", prefix) & filters.group)
@use_chat_lang()
async def mentionadmins(c: Client, m: Message, strings):
    mention = ""
    async for i in c.iter_chat_members(m.chat.id, filter="administrators"):
        if not (i.user.is_deleted or i.is_anonymous):
            mention += f"{i.user.mention}\n"
    await c.send_message(
        m.chat.id,
        strings("admins_list").format(chat_title=m.chat.title, admins_list=mention),
    )


@Client.on_message(
    (filters.command("report", prefix) | filters.regex("^@admin"))
    & filters.group
    & filters.reply
)
@use_chat_lang()
async def reportadmins(c: Client, m: Message, strings):
    if m.reply_to_message.from_user:
        check_admin = await c.get_chat_member(
            m.chat.id, m.reply_to_message.from_user.id
        )
        if check_admin.status not in admin_status:
            mention = ""
            async for i in c.iter_chat_members(m.chat.id, filter="administrators"):
                if not (i.user.is_deleted or i.is_anonymous or i.user.is_bot):
                    mention += f"<a href='tg://user?id={i.user.id}'>\u2063</a>"
            await m.reply_to_message.reply_text(
                strings("report_admns").format(
                    admins_list=mention,
                    reported_user=m.reply_to_message.from_user.mention(),
                ),
            )


@Client.on_message(filters.command("token"))
@use_chat_lang()
async def getbotinfo(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("no_bot_token"), reply_to_message_id=m.message_id
        )
    text = m.text.split(maxsplit=1)[1]
    req = await http.get(f"https://api.telegram.org/bot{text}/getme")
    fullres = req.json()
    if not fullres["ok"]:
        await m.reply(strings("bot_token_invalid"))
    else:
        res = fullres["result"]
        get_bot_info_text = strings("bot_token_info")
    await m.reply(
        get_bot_info_text.format(
            botname=res["first_name"], botusername=res["username"], botid=res["id"]
        ),
        reply_to_message_id=m.message_id,
    )


@Client.on_message(filters.reply & filters.group & filters.regex(r"(?i)^rt$"))
async def rtcommand(c: Client, m: Message):
    rt_text = None
    if m.reply_to_message.media:
        rt_text = m.reply_to_message.caption
    else:
        rt_text = m.reply_to_message.text

    if rt_text is None:
        return

    if not re.match("🔃 .* retweeted:\n\n👤 .*", rt_text):
        text = f"🔃 <b>{escape(m.from_user.first_name)}</b> retweeted:\n\n"
        text += f"👤 <b>{escape(m.reply_to_message.from_user.first_name)}</b>:"
        text += f" <i>{escape(rt_text)}</i>"

        await m.reply_to_message.reply_text(
            text,
            disable_web_page_preview=True,
            disable_notification=True,
        )


@Client.on_message(filters.command("urlencode", prefix))
async def urlencodecmd(c: Client, m: Message):
    await m.reply_text(quote(m.text.split(None, 1)[1]))


@Client.on_message(filters.command("urldecode", prefix))
async def urldecodecmd(c: Client, m: Message):
    await m.reply_text(unquote(m.text.split(None, 1)[1]))


@Client.on_message(filters.command("bug", prefix))
@use_chat_lang()
async def bug_report_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        try:
            bug_report = (
                "<b>Bug Report</b>\n"
                f"User: {m.from_user.mention}\n"
                f"ID: <code>{m.from_user.id}</code>\n\n"
                "The content of the report:\n"
                f"<code>{escape(m.text.split(None, 1)[1])}</code>"
            )
            await c.send_message(
                chat_id=log_chat,
                text=bug_report,
                disable_web_page_preview=True,
            )
            await m.reply_text(strings("bug_reported_success_to_bot_admins"))
        except BadRequest:
            await m.reply_text(strings("err_cant_send_bug_report_to_bot_admins"))
    else:
        await m.reply(strings("err_no_bug_to_report"))


@Client.on_message(filters.command("request", prefix))
async def request_cmd(c: Client, m: Message):
    if len(m.text.split()) > 1:
        text = m.text.split(maxsplit=1)[1]
        if re.match(r"^(https?)://", text):
            url = text
        else:
            url = "http://" + text
        req = await http.get(url)
        headers = "<b>{}</b> <code>{} {}</code>\n".format(
            req.extensions.get("http_version").decode(),
            req.status_code,
            req.extensions.get("reason_phrase", b"").decode(),
        )
        headers += "\n".join(
            "<b>{}:</b> <code>{}</code>".format(x.title(), escape(req.headers[x]))
            for x in req.headers
        )
        await m.reply_text(f"<b>Headers:</b>\n{headers}")
    else:
        await m.reply_text(
            "You must specify the url, E.g.: <code>/request https://example.com</code>"
        )


@Client.on_message(filters.command("parsebutton"))
@use_chat_lang()
async def button_parse_helper(c: Client, m: Message, strings):
    if len(m.text.split()) > 2:
        await m.reply_text(
            f"[{m.text.split(None, 2)[2]}](buttonurl:{m.command[1]})", parse_mode=None
        )
    else:
        await m.reply_text(strings("parsebtn_err"))


@Client.on_message(filters.command("donate", prefix))
@use_chat_lang()
async def donatecmd(c: Client, m: Message, strings):
    await m.reply(strings("donatecmdstring"))


commands.add_command("mark", "general")
commands.add_command("html", "general")
commands.add_command("admins", "general")
commands.add_command("token", "general")
commands.add_command("urlencode", "general")
commands.add_command("urldecode", "general")
commands.add_command("parsebutton", "general")
commands.add_command("donate", "general")
