# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from datetime import datetime
from re import TEMPLATE

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from eduu.utils.localization import use_chat_lang


from ..config import PREFIXES
from ..utils import commands, http

url_reddit = "http://www.reddit.com/r/{0}/.json?limit=6"
headers = {
    'User-agent': 'testscript by /u/fakebot3'
}
LIMIT_CHARACTERS = 25
TEMPLATE_MSG = "[{title}]({link_by_subreddit})\n\n{feed}`"
TEMPLATE_POST = "`> `[{title}]({pUrl})` <{nsfw}> - `[{comments}]({permalink})\n"


def treatTitle(title):
    title = title.replace("_", " ")
    title = title.replace("[", "(")
    title = title.replace("]", ")")
    title = title.replace("(", "(")
    title = title.replace(")", ")")
    return title


def limitLength(title):
    if len(title) > LIMIT_CHARACTERS:
        return title[:LIMIT_CHARACTERS] + "..."
    else:
        return title


@Client.on_message(filters.command("reddit", PREFIXES))
@use_chat_lang()
async def reddit(c: Client, m: Message, strings):
    text_command = m.text.split(" ", 1)
    if text_command.__len__() > 1:
        subreddit = text_command[1]
        subreddit_link = "http://www.reddit.com/" + subreddit
        response = await http.get(url_reddit.format(subreddit), headers=headers, follow_redirects=True)
        data = response.json()
        feed = ""

        if response.status_code == 200:
            for post in data['data']['children']:
                title_post = limitLength(treatTitle(post['data']['title']))
                purl = post['data']['url']
                permalink = "http://www.reddit.com" + post['data']['permalink']
                is_nsfw = "NSFW" if post['data']['over_18'] else "SFW"
                post_item = TEMPLATE_POST.format(
                    title=title_post,
                    permalink=permalink,
                    nsfw=is_nsfw,
                    pUrl=purl,
                    comments=strings("reddit_comment").format(
                        post['data']['num_comments'])
                )
                feed += post_item

            if feed:
                post_formatted = TEMPLATE_MSG.format(
                    link_by_subreddit=subreddit_link,
                    title="r/" + subreddit,
                    feed=feed
                )
                await m.reply_text(post_formatted, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            elif response.status_code == 404 or response.status_code == 403:
                await m.reply_text(strings("reddit_not_found"))
            else:
                await m.reply_text(strings("reddit_error"))
    else:
        await m.reply_text(strings("command_not_found"), parse_mode=ParseMode.HTML)


commands.add_command("reddit", "general")
