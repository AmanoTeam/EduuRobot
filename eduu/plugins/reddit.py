# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from html import escape

from hydrogram import Client, filters
from hydrogram.types import Message

from config import PREFIXES
from eduu.utils import commands, http
from eduu.utils.localization import Strings, use_chat_lang

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

    feed_items = []
    for post in data["data"]["children"]:
        post_url = post["data"]["url"]
        post_title = escape(limit_length(post["data"]["title"]))
        nsfw = "NSFW" if post["data"]["over_18"] else "SFW"
        comments = s("reddit_comments").format(post["data"]["num_comments"])

        post_item = f" - <a href='{post_url}'>{post_title}</a> &lt;{nsfw}&gt; - <a href='{post_url}'>{comments}</a>"
        feed_items.append(post_item)

    if not feed_items:
        await m.reply_text(s("reddit_no_results"))
        return

    feed = "\n".join(feed_items)

    await m.reply_text(
        f"<a href='https://www.reddit.com/r/{subreddit}'>r/{subreddit}</a>\n\n{feed}",
        disable_web_page_preview=True,
    )


commands.add_command("reddit", "tools", aliases=["r"])
