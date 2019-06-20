# Copyright (C) 2018-2019 Amano Team <contact@amanoteam.ml>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import re
import urllib

import aiohttp

from config import bot


def treattitle(title):
    title = title.replace("_", " ")
    title = title.replace("[", "(")
    title = title.replace("]", ")")
    title = title.replace("(", "(")
    title = title.replace(")", ")")
    return title


async def reddit(msg):
    if msg.get('text'):
        if msg['text'].split()[0] == '/r' or msg['text'].split()[0] == '!r':
            sub = msg['text'][3:]
            if sub:
                sub = re.findall(r'\S*', sub)
                sub = "r/" + sub[0] if sub[0:2] != "r/" else sub[0]
                url = "http://www.reddit.com/" + sub + "/.json?limit=6"
                subreddit = "http://www.reddit.com/" + sub
                async with aiohttp.ClientSession() as session:
                    request = await session.get(url, headers={'User-agent': 'testscript by /u/fakebot3'})
                    data = await request.json()
                posts = ""
                if request.status == 200:
                    for post in data['data']['children']:
                        domain = post['data']['domain']
                        title = treattitle(post['data']['title'])
                        purl = urllib.parse.quote_plus(post['data']['url'])
                        isnsfw_bool = post['data']['over_18']
                        permalink = "http://www.reddit.com" + post['data']['permalink']
                        if isnsfw_bool:
                            isnsfw = "nsfw"
                        else:
                            isnsfw = "sfw"
                        post = u"`> `[{title}]({pUrl})` <{nsfw}> - `[comments]({permalink})\n".format(title=title,
                                                                                                      permalink=permalink,
                                                                                                      nsfw=isnsfw,
                                                                                                      pUrl=purl,
                                                                                                      domain=domain)
                        posts += post
                    if posts:
                        await bot.sendMessage(msg['chat']['id'],
                                              "[{sub}]({subreddit})`:`\n\n".format(sub=sub,
                                                                                   subreddit=subreddit) + posts,
                                              reply_to_message_id=msg['message_id'], parse_mode="Markdown",
                                              disable_web_page_preview=True)
                    else:
                        await bot.sendMessage(msg['chat']['id'],
                                              u"`I couldnt find {sub}, please try again`".format(sub=sub),
                                              reply_to_message_id=msg['message_id'], parse_mode="Markdown",
                                              disable_web_page_preview=True)
                elif request.status_code == 403:
                    await bot.sendMessage(msg['chat']['id'], "`Subreddit not found, please verify your input.`",
                                          reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                else:
                    await bot.sendMessage(msg['chat']['id'],
                                          f"`There has been an error, the number {request.status_code} to be specific.`",
                                          reply_to_message_id=msg['message_id'],
                                          parse_mode="Markdown")
            else:
                await bot.sendMessage(msg['chat']['id'],
                                      "`Follow this command with the name of a subreddit to see the top 6 posts.\nExample: /r Awww`",
                                      parse_mode="Markdown", reply_to_message_id=msg['message_id'])
            return True
