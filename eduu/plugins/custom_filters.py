# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import re

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, Message

from config import PREFIXES
from eduu.database.custom_filters import (
    add_filter,
    get_all_filters,
    rm_filter,
    update_filter,
)
from eduu.utils import button_parser, commands, split_quotes
from eduu.utils.decorators import require_admin
from eduu.utils.localization import use_chat_lang


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
async def save_filter(c: Client, m: Message, strings):
    args = m.text.markdown.split(maxsplit=1)
    split_text = split_quotes(args[1])
    trigger = split_text[0].lower()

    if m.reply_to_message is None and len(split_text) < 2:
        await m.reply_text(strings("add_filter_empty"), quote=True)
        return

    if m.reply_to_message and m.reply_to_message.photo:
        file_id = m.reply_to_message.photo.file_id
        raw_data = (
            m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        )
        filter_type = "photo"
    elif m.reply_to_message and m.reply_to_message.document:
        file_id = m.reply_to_message.document.file_id
        raw_data = (
            m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        )
        filter_type = "document"
    elif m.reply_to_message and m.reply_to_message.video:
        file_id = m.reply_to_message.video.file_id
        raw_data = (
            m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        )
        filter_type = "video"
    elif m.reply_to_message and m.reply_to_message.audio:
        file_id = m.reply_to_message.audio.file_id
        raw_data = (
            m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        )
        filter_type = "audio"
    elif m.reply_to_message and m.reply_to_message.animation:
        file_id = m.reply_to_message.animation.file_id
        raw_data = (
            m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        )
        filter_type = "animation"
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
    await m.reply_text(strings("add_filter_success").format(trigger=trigger), quote=True)


@Client.on_message(filters.command(["delfilter", "rmfilter", "stop"], PREFIXES))
@require_admin(allow_in_private=True)
@use_chat_lang
async def delete_filter(c: Client, m: Message, strings):
    args = m.text.markdown.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    check_filter = await check_for_filters(chat_id, trigger)

    if not check_filter:
        await m.reply_text(strings("no_filter_with_name").format(trigger=trigger), quote=True)
        return

    await rm_filter(chat_id, trigger)
    await m.reply_text(strings("remove_filter_success").format(trigger=trigger), quote=True)


@Client.on_message(filters.command("filters", PREFIXES))
@use_chat_lang
async def get_all_filter(c: Client, m: Message, strings):
    chat_id = m.chat.id
    reply_text = strings("filters_list")
    all_filters = await get_all_filters(chat_id)
    for filter_s in all_filters:
        keyword = filter_s[1]
        reply_text += f" - {keyword} \n"

    if not all_filters:
        await m.reply_text(strings("filters_list_empty"), quote=True)
        return

    await m.reply_text(reply_text, quote=True)


@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming, group=1)
async def serve_filter(c: Client, m: Message):
    chat_id = m.chat.id
    text = m.text
    targeted_message = m.reply_to_message or m

    all_filters = await get_all_filters(chat_id)
    for filter in all_filters:
        keyword = filter[1]
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if not re.search(pattern, text, flags=re.IGNORECASE):
            continue

        data, button = button_parser(filter[2])
        if filter[4] == "text":
            await targeted_message.reply_text(
                data,
                quote=True,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )
        elif filter[4] == "photo":
            await targeted_message.reply_photo(
                filter[3],
                quote=True,
                caption=data,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )

        elif filter[4] == "document":
            await targeted_message.reply_document(
                filter[3],
                quote=True,
                caption=data,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )

        elif filter[4] == "video":
            await targeted_message.reply_video(
                filter[3],
                quote=True,
                caption=data,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )

        elif filter[4] == "audio":
            await targeted_message.reply_audio(
                filter[3],
                quote=True,
                caption=data,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )

        elif filter[4] == "animation":
            await targeted_message.reply_animation(
                filter[3],
                quote=True,
                caption=data,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )

        elif filter[4] == "sticker":
            await targeted_message.reply_sticker(
                filter[3],
                quote=True,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )


commands.add_command("delfilter", "admin")
commands.add_command("filter", "admin")
commands.add_command("filters", "general")
