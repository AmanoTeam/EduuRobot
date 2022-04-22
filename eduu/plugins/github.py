# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from urllib.parse import quote_plus

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands, http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command(["github", "gh", "git"], prefix))
@use_chat_lang()
async def git(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("github_usage"), reply_to_message_id=m.message_id
        )

    text = m.text.split(maxsplit=1)[1]
    req = await http.get(f"https://api.github.com/users/{text}")
    res = req.json()

    if not res.get("login"):
        return await m.reply_text(
            strings("github_user_not_found"), reply_to_message_id=m.message_id
        )

    avatar = res["avatar_url"]

    anticache = quote_plus((await http.head(avatar)).headers["Last-Modified"])

    caption_text = strings("info_git_user")
    await m.reply_photo(
        avatar + anticache,
        caption=caption_text.format(
            name=res["name"],
            username=res["login"],
            location=res["location"],
            type=res["type"],
            bio=res["bio"],
        ),
        reply_to_message_id=m.message_id,
    )


commands.add_command("github", "tools")
