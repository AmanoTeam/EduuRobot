# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import re

from hydrogram import Client, filters
from hydrogram.enums import ParseMode
from hydrogram.types import InlineKeyboardMarkup, Message

from config import PREFIXES
from eduu.database.custom_filters import (
    add_filter,
    get_all_filters,
    rm_filter,
    update_filter,
)
from eduu.utils import button_parser, commands, split_quotes
from eduu.utils.decorators import require_admin
from eduu.utils.localization import Strings, use_chat_lang


async def check_for_filters(chat_id, trigger):
    all_filters = await get_all_filters(chat_id)
    for keywords in all_filters:
        keyword = keywords[1]
        if trigger == keyword:
            return True
    return False


@Client.on_message(filters.command(["filter", "savefilter"], PREFIXES))
@require_admin(allow_in_private=True)
@use_chat_lang
async def save_filter(c: Client, m: Message, s: Strings):
    args = m.text.markdown.split(maxsplit=1)
    split_text = split_quotes(args[1])
    trigger = split_text[0].lower()

    if m.reply_to_message is None and len(split_text) < 2:
        await m.reply_text(s("filters_add_empty"), quote=True)
        return

    if m.reply_to_message.media and m.reply_to_message.media.value in (
        "photo", "document", "video", "audio", "animation"
    ):
        file_id = getattr(m.reply_to_message, m.reply_to_message.media.value).file_id
        raw_data = (
            m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        )
        filter_type = m.reply_to_message.media.value
    elif m.reply_to_message and m.reply_to_message.sticker:
        file_id = m.reply_to_message.sticker.file_id
        raw_data = split_text[1] if len(split_text) > 1 else None
        filter_type = "sticker"
    else:
        file_id = None
        raw_data = split_text[1]
        filter_type = "text"

    chat_id = m.chat.id
    check_filter = await check_for_filters(chat_id, trigger)

    if check_filter:
        await update_filter(chat_id, trigger, raw_data, file_id, filter_type)
    else:
        await add_filter(chat_id, trigger, raw_data, file_id, filter_type)

    await m.reply_text(s("filters_add_success").format(trigger=trigger), quote=True)


@Client.on_message(filters.command(["delfilter", "rmfilter", "stop"], PREFIXES))
@require_admin(allow_in_private=True)
@use_chat_lang
async def delete_filter(c: Client, m: Message, s: Strings):
    args = m.text.markdown.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    check_filter = await check_for_filters(chat_id, trigger)

    if not check_filter:
        await m.reply_text(s("filters_no_filter_with_name").format(trigger=trigger), quote=True)
        return

    await rm_filter(chat_id, trigger)
    await m.reply_text(s("filters_remove_success").format(trigger=trigger), quote=True)


@Client.on_message(filters.command("filters", PREFIXES))
@use_chat_lang
async def get_all_filter(c: Client, m: Message, s: Strings):
    chat_id = m.chat.id
    reply_text = s("filters_list")
    all_filters = await get_all_filters(chat_id)
    for filter_s in all_filters:
        keyword = filter_s[1]
        reply_text += f" - {keyword} \n"

    if not all_filters:
        await m.reply_text(s("filters_list_empty"), quote=True)
        return

    await m.reply_text(reply_text, quote=True)


@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming, group=1)
async def serve_filter(c: Client, m: Message):
    chat_id = m.chat.id
    text = m.text
    targeted_message = m.reply_to_message or m

    all_filters = await get_all_filters(chat_id)
    for filter_ in all_filters:
        keyword = filter_[1]
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if not re.search(pattern, text, flags=re.IGNORECASE):
            continue

        data, button = button_parser(filter_[2])
        if filter_[4] == "text":
            await targeted_message.reply_text(
                data,
                quote=True,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )
        elif filter_[4] in ("photo", "document", "video", "audio", "animation", "sticker"):
            await targeted_message.reply_cached_media(
                filter_[3],
                quote=True,
                caption=data,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )


commands.add_command("delfilter", "admin")
commands.add_command("filter", "admin")
commands.add_command("filters", "general")
