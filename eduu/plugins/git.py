# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from urllib.parse import quote_plus

from hydrogram import Client, filters
from hydrogram.types import Message

from config import PREFIXES
from eduu.utils import commands, http
from eduu.utils.localization import Strings, use_chat_lang


@Client.on_message(filters.command("git", PREFIXES))
@use_chat_lang
async def git(c: Client, m: Message, s: Strings):
    if len(m.command) == 1:
        await m.reply_text(s("git_no_username"), reply_to_message_id=m.id)
        return

    text = m.text.split(maxsplit=1)[1]
    req = await http.get(f"https://api.github.com/users/{text}")
    res = req.json()

    if not res.get("login"):
        await m.reply_text(s("git_user_not_found"), reply_to_message_id=m.id)
        return

    avatar = res["avatar_url"]

    anticache = quote_plus((await http.head(avatar)).headers["Last-Modified"])

    caption_text = s("git_user_info")
    await m.reply_photo(
        avatar + anticache,
        caption=caption_text.format(
            name=res["name"],
            username=res["login"],
            location=res["location"],
            type=res["type"],
            bio=res["bio"],
        ),
        reply_to_message_id=m.id,
    )


commands.add_command("git", "tools")
