# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import uuid
from json import JSONDecodeError

from httpx import HTTPError
from pyrogram import Client, filters
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from ..config import PREFIXES
from ..utils import commands, http
from ..utils.localization import use_chat_lang


@Client.on_message(filters.command("print", PREFIXES))
@use_chat_lang()
async def prints(c: Client, m: Message, strings):
    # Get the target URl from the message using Telegram entities.
    # If there is no URL, try to get an URL from the replied message.
    # If there is no URL in the replied message, fail.

    for entity in m.entities or m.caption_entities:
        if entity.type == MessageEntityType.URL:
            if m.text:
                target_url = m.text[entity.offset : entity.offset + entity.length]
            else:
                target_url = m.caption[entity.offset : entity.offset + entity.length]
            break
        if entity.type == MessageEntityType.TEXT_LINK:
            target_url = entity.url
            break
    else:
        if m.reply_to_message:
            for entity in (
                m.reply_to_message.entities or m.reply_to_message.caption_entities
            ):
                if entity.type == MessageEntityType.URL:
                    if m.reply_to_message.text:
                        target_url = m.reply_to_message.text[
                            entity.offset : entity.offset + entity.length
                        ]
                    else:
                        target_url = m.reply_to_message.caption[
                            entity.offset : entity.offset + entity.length
                        ]
                    break
                if entity.type == MessageEntityType.TEXT_LINK:
                    target_url = entity.url
                    break
            else:
                await m.reply_text(strings("print_usage"))
                return
        else:
            await m.reply_text(strings("print_usage"))
            return

    sent = await m.reply_text(strings("taking_screenshot"))

    try:
        response = await screenshot_page(target_url)
    except BaseException as e:
        await sent.edit_text(f"<b>API returned an error:</b> <code>{e}</code>")
        return

    if response:
        try:
            await m.reply_photo(response)
            await sent.delete()
        except BaseException:
            # if failed to send the message, it's not API's
            # fault.
            # most probably there are some other kind of problem,
            # for example it failed to delete its message.
            # or the bot doesn't have access to send media in the chat.
            return
    else:
        await m.reply_text(
            "Couldn't get url value, most probably API is not accessible."
        )


async def screenshot_page(target_url: str) -> str:
    """
    This function is used to get a screenshot of a website using htmlcsstoimage.com API.

    :param target_url: The URL of the website to get a screenshot of.
    :return: The URL of the screenshot.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
    }

    data = {
        "url": target_url,
        # Sending a random CSS to make the API to generate a new screenshot.
        "css": f"random-tag: {uuid.uuid4()}",
        "render_when_ready": False,
        "viewport_width": 1280,
        "viewport_height": 720,
        "device_scale": 1,
    }

    try:
        resp = await http.post(
            "https://htmlcsstoimage.com/demo_run", headers=headers, json=data
        )
        return resp.json()["url"]
    except (JSONDecodeError, KeyError) as e:
        raise Exception("Screenshot API returned an invalid response.") from e
    except (KeyError, HTTPError) as e:
        raise Exception("Screenshot API seems offline. Try again later.") from e


commands.add_command("print", "tools")
