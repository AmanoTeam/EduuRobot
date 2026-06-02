# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2026 Amano LLC

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

from hydrogram import Client, filters

from config import PREFIXES
from eduu.utils import commands, http
from eduu.utils.localization import Strings, use_chat_lang

if TYPE_CHECKING:
    from hydrogram.types import Message

CHARACTER_LIMIT = 25


def limit_length(title: str):
    if len(title) > CHARACTER_LIMIT:
        return f"{title[:CHARACTER_LIMIT].rstrip()}…"

    return title


@Client.on_message(filters.command(["reddit", "r"], PREFIXES))
@use_chat_lang
async def reddit(c: Client, m: Message, s: Strings):
    if len(m.command) == 1:
        await m.reply_text(s("reddit_usage"))
        return

    subreddit = m.command[1]

    r = await http.get(f"https://www.reddit.com/r/{subreddit}/.json?limit=6")

    if r.status_code in {404, 403}:
        await m.reply_text(s("reddit_not_found"))
        return

    if r.status_code >= 300:
        await m.reply_text(s("reddit_error"))
        return

    data = r.json()

    feed_items = [
        (
            f" - <a href='{post['data']['url']}'>"
            f"{escape(limit_length(post['data']['title']))}</a>"
            f" &lt;{'NSFW' if post['data']['over_18'] else 'SFW'}&gt; - "
            f"<a href='{post['data']['url']}'>"
            f"{s('reddit_comments').format(post['data']['num_comments'])}</a>"
        )
        for post in data["data"]["children"]
    ]

    if not feed_items:
        await m.reply_text(s("reddit_no_results"))
        return

    feed = "\n".join(feed_items)

    await m.reply_text(
        f"<a href='https://www.reddit.com/r/{subreddit}'>r/{subreddit}</a>\n\n{feed}",
        disable_web_page_preview=True,
    )


commands.add_command("reddit", "tools", aliases=["r"])
