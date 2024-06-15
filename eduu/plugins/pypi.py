# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import html
import re

from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import PREFIXES
from eduu.utils import commands, http
from eduu.utils.localization import Strings, use_chat_lang


def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    return re.sub(cleanr, "", raw_html)


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition


@Client.on_message(filters.command("pypi", PREFIXES))
@use_chat_lang
async def pypi(c: Client, m: Message, s: Strings):
    if len(m.command) == 1:
        await m.reply_text(s("pypi_usage"))
        return

    text = m.text.split(maxsplit=1)[1]
    r = await http.get(f"https://pypi.org/pypi/{text}/json", follow_redirects=True)
    if r.status_code != 200:
        await m.reply_text(
            s("pypi_package_not_found").format(package_name=text, http_status=r.status_code)
        )
        return

    json = r.json()
    pypi_info = escape_definition(json["info"])

    message = s("pypi_package_details").format(
        package_name=pypi_info["name"],
        author_name=pypi_info["author"],
        author_email=f"&lt;{pypi_info['author_email']}&gt;" if pypi_info["author_email"] else "",
        platform=pypi_info["platform"] or s("pypi_platform_not_specified"),
        version=pypi_info["version"],
        license=pypi_info["license"] or s("pypi_platform_not_specified"),
        summary=pypi_info["summary"],
    )

    if pypi_info["home_page"] and pypi_info["home_page"] != "UNKNOWN":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=s("pypi_package_home_page"),
                        url=pypi_info["home_page"],
                    )
                ]
            ]
        )
    else:
        kb = None
    await m.reply_text(message, disable_web_page_preview=True, reply_markup=kb)


commands.add_command("pypi", "tools")
