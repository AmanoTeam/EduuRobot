# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2018-2021 Amano Team

import ujson as json

from httpx import HTTPError

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands
from eduu.utils.consts import http
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("print", prefix))
@use_chat_lang()
async def prints(c: Client, message: Message, strings):
    msg = message.text
    the_url = msg.split(" ", 1)
    wrong = False

    if len(the_url) == 1:
        if message.reply_to_message:
            the_url = message.reply_to_message.text
            if len(the_url) == 1:
                wrong = True
            else:
                the_url = the_url[1]
        else:
            wrong = True
    else:
        the_url = the_url[1]

    if wrong:
        await message.reply_text("Format : [!, /]print < your url > (or reply to a message)")
        return

    try:
        sent = await message.reply_text(strings("taking_screenshot"))
        res_json = await cssworker_url(target_url=the_url)
    except BaseException as e:
        await message.reply(f"**Failed due to:** `{e}`")
        return

    if res_json:
        # {"url":"image_url","response_time":"147ms"}
        image_url = res_json["url"]
        if image_url:
            try:
                await message.reply_photo(image_url)
                await sent.delete()
            except BaseException:
                # if failed to send the message, it's not API's
                # fault.
                # most probably there are some other kind of problem,
                # for example it failed to delete its message.
                # or the bot doesn't have access to send media in the chat.
                return
        else:
            await message.reply("couldn't get url value, most probably API is not accessible.")
    else:
        await message.reply("Failed, because API is not responding, try it later.")



async def cssworker_url(target_url: str):
    url = "https://htmlcsstoimage.com/demo_run"
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://htmlcsstoimage.com/',
        'Content-Type': 'application/json',
        'Origin': 'https://htmlcsstoimage.com',
        'Alt-Used': 'htmlcsstoimage.com',
        'Connection': 'keep-alive',
    }

    # remove 'https' prefixes to avoid bugging out api
    target_url = target_url.lstrip("https://")
    target_url = target_url.rstrip("http://")

    data = json.dumps({"html": "", "console_mode": "", "url": target_url, "css": "", "selector": "", "ms_delay": "",
                    "render_when_ready": "false", "viewport_height": "", "viewport_width": "",
                    "google_fonts": "", "device_scale": ""})

    try:
        resp = await http.post(url, data=data, headers=my_headers)
        return resp.json()
    except HTTPError:
        return None



commands.add_command("print", "tools")
