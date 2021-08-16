# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import html
import re

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from eduu.config import prefix
from eduu.utils import commands
from eduu.utils.consts import http
from eduu.utils.localization import use_chat_lang
from eduu.utils.bot_error_log import logging_errors


def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition


@Client.on_message(filters.command("pypi", prefix))
@use_chat_lang()
@logging_errors
async def pypi(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("pypi_usage"))

    text = m.text.split(maxsplit=1)[1]
    r = await http.get(f"https://pypi.org/pypi/{text}/json")
    if r.status_code == 200:
        json = r.json()
        pypi_info = escape_definition(json["info"])

        message = strings("package_details").format(
            package_name=pypi_info["name"],
            author_name=pypi_info["author"],
            author_email=f"&lt;{pypi_info['author_email']}&gt;"
            if pypi_info["author_email"]
            else "",
            platform=pypi_info["platform"] or strings("not_specified"),
            version=pypi_info["version"],
            license=pypi_info["license"] or strings("not_specified"),
            summary=pypi_info["summary"],
        )

        if pypi_info["home_page"] and pypi_info["home_page"] != "UNKNOWN":
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=strings("package_home_page"),
                            url=pypi_info["home_page"],
                        )
                    ]
                ]
            )
        else:
            kb = None
        await m.reply_text(message, disable_web_page_preview=True, reply_markup=kb)
    else:
        await m.reply_text(
            strings("package_not_found").format(
                package_name=text, http_status=r.status_code
            )
        )


commands.add_command("pypi", "tools")
