# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import re
from html import escape
from urllib.parse import quote, unquote

from hydrogram import Client, filters
from hydrogram.enums import ChatMembersFilter, ParseMode
from hydrogram.errors import BadRequest
from hydrogram.types import InlineKeyboardMarkup, Message

from config import LOG_CHAT, PREFIXES
from eduu.utils import button_parser, commands, http
from eduu.utils.consts import ADMIN_STATUSES
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("mark", PREFIXES))
@use_chat_lang
async def mark(c: Client, m: Message, strings):
    if len(m.command) == 1:
        await m.reply_text(strings("mark_usage"))
        return

    txt = m.text.split(None, 1)[1]
    msgtxt, buttons = button_parser(txt)
    await m.reply_text(
        msgtxt,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=(InlineKeyboardMarkup(buttons) if len(buttons) != 0 else None),
    )


@Client.on_message(filters.command("html", PREFIXES))
@use_chat_lang
async def html(c: Client, m: Message, strings):
    if len(m.command) == 1:
        await m.reply_text(strings("html_usage"))
        return

    txt = m.text.split(None, 1)[1]
    msgtxt, buttons = button_parser(txt)
    await m.reply_text(
        msgtxt,
        parse_mode=ParseMode.HTML,
        reply_markup=(InlineKeyboardMarkup(buttons) if len(buttons) != 0 else None),
    )


@Client.on_message(filters.command("admins", PREFIXES) & filters.group)
@use_chat_lang
async def mentionadmins(c: Client, m: Message, strings):
    mention = ""
    async for i in m.chat.get_members(m.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        if not (i.user.is_deleted or i.privileges.is_anonymous):
            mention += f"{i.user.mention}\n"
    await c.send_message(
        m.chat.id,
        strings("admins_list").format(chat_title=m.chat.title, admins_list=mention),
    )


@Client.on_message(
    (filters.command(["report", "reportar"], PREFIXES) | filters.regex("^@admin"))
    & filters.group
    & filters.reply
)
@use_chat_lang
async def reportadmins(c: Client, m: Message, strings):
    if not m.reply_to_message.from_user:
        return

    check_admin = await m.chat.get_member(m.reply_to_message.from_user.id)
    if check_admin.status in ADMIN_STATUSES:
        return

    mention = ""
    async for i in m.chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS):
        if not (i.user.is_deleted or i.privileges.is_anonymous or i.user.is_bot):
            mention += f"<a href='tg://user?id={i.user.id}'>\u2063</a>"
    await m.reply_to_message.reply_text(
        strings("report_admns").format(
            admins_list=mention,
            reported_user=m.reply_to_message.from_user.mention(),
        ),
    )


@Client.on_message(filters.command("token"))
@use_chat_lang
async def getbotinfo(c: Client, m: Message, strings):
    if len(m.command) == 1:
        await m.reply_text(strings("no_bot_token"), reply_to_message_id=m.id)
        return

    text = m.text.split(maxsplit=1)[1]
    req = await http.get(f"https://api.telegram.org/bot{text}/getme")
    fullres = req.json()
    if not fullres["ok"]:
        await m.reply_text(strings("bot_token_invalid"))
    else:
        res = fullres["result"]
        get_bot_info_text = strings("bot_token_info")
    await m.reply_text(
        get_bot_info_text.format(
            botname=res["first_name"], botusername=res["username"], botid=res["id"]
        ),
        reply_to_message_id=m.id,
    )


@Client.on_message(filters.reply & filters.group & filters.regex(r"(?i)^rt$"))
async def rtcommand(c: Client, m: Message):
    rt_text = None
    rt_text = m.reply_to_message.caption if m.reply_to_message.media else m.reply_to_message.text

    if rt_text is None or re.match("🔃 .* retweeted:\n\n👤 .*", rt_text):
        return

    text = f"🔃 <b>{escape(m.from_user.first_name)}</b> retweeted:\n\n"
    text += f"👤 <b>{escape(m.reply_to_message.from_user.first_name)}</b>:"
    text += f" <i>{escape(rt_text)}</i>"

    await m.reply_to_message.reply_text(
        text,
        disable_web_page_preview=True,
        disable_notification=True,
    )


@Client.on_message(filters.command("urlencode", PREFIXES))
async def urlencodecmd(c: Client, m: Message):
    await m.reply_text(quote(m.text.split(None, 1)[1]))


@Client.on_message(filters.command("urldecode", PREFIXES))
async def urldecodecmd(c: Client, m: Message):
    await m.reply_text(unquote(m.text.split(None, 1)[1]))


@Client.on_message(filters.command("bug", PREFIXES))
@use_chat_lang
async def bug_report_cmd(c: Client, m: Message, strings):
    if len(m.text.split()) == 1:
        await m.reply_text(strings("err_no_bug_to_report"))
        return

    try:
        bug_report = (
            "<b>Bug Report</b>\n"
            f"User: {m.from_user.mention}\n"
            f"ID: <code>{m.from_user.id}</code>\n\n"
            "The content of the report:\n"
            f"<code>{escape(m.text.split(None, 1)[1])}</code>"
        )
        await c.send_message(
            chat_id=LOG_CHAT,
            text=bug_report,
            disable_web_page_preview=True,
        )
        await m.reply_text(strings("bug_reported_success_to_bot_admins"))
    except BadRequest:
        await m.reply_text(strings("err_cant_send_bug_report_to_bot_admins"))


@Client.on_message(filters.command("request", PREFIXES))
async def request_cmd(c: Client, m: Message):
    if len(m.text.split()) == 1:
        await m.reply_text(
            "You must specify the url, E.g.: <code>/request https://example.com</code>"
        )
        return

    text = m.text.split(maxsplit=1)[1]
    url = text if re.match(r"^(https?)://", text) else f"http://{text}"
    req = await http.get(url)
    headers = f'<b>{req.extensions.get("http_version").decode()}</b> <code>{req.status_code} {req.extensions.get("reason_phrase", b"").decode()}</code>\n'

    headers += "\n".join(
        f"<b>{x.title()}:</b> <code>{escape(req.headers[x])}</code>" for x in req.headers
    )

    await m.reply_text(f"<b>Headers:</b>\n{headers}")


@Client.on_message(filters.command("parsebutton"))
@use_chat_lang
async def button_parse_helper(c: Client, m: Message, strings):
    if len(m.text.split()) > 2:
        await m.reply_text(
            f"[{m.text.split(None, 2)[2]}](buttonurl:{m.command[1]})",
            parse_mode=ParseMode.DISABLED,
        )
    else:
        await m.reply_text(strings("parsebtn_err"))


@Client.on_message(filters.command("donate", PREFIXES))
@use_chat_lang
async def donatecmd(c: Client, m: Message, strings):
    await m.reply_text(strings("donatecmdstring"))


commands.add_command("mark", "general")
commands.add_command("html", "general")
commands.add_command("admins", "general")
commands.add_command("token", "general")
commands.add_command("urlencode", "general")
commands.add_command("urldecode", "general")
commands.add_command("parsebutton", "general")
commands.add_command("donate", "general")
