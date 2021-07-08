# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import re
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, Message

from eduu.config import prefix
from eduu.database import filters as filtersdb
from eduu.utils import button_parser, commands, require_admin, split_quotes
from eduu.utils.localization import use_chat_lang


async def add_filter(
    chat_id: int,
    trigger,
    filter_type,
    raw_data: Optional[str] = None,
    file_id: Optional[str] = None,
):
    await filtersdb.create(
        chat_id=chat_id,
        filter_name=trigger,
        raw_data=raw_data,
        file_id=file_id,
        filter_type=filter_type,
    )


async def update_filter(
    chat_id: int,
    trigger,
    filter_type,
    raw_data: Optional[str] = None,
    file_id: Optional[str] = None,
):
    await filtersdb.filter(chat_id=chat_id, filter_name=trigger).update(
        raw_data=raw_data, file_id=file_id, filter_type=filter_type
    )


async def rm_filter(chat_id: int, trigger):
    await filtersdb.filter(chat_id=chat_id, filter_name=trigger).delete()


async def get_all_filters(chat_id: int):
    return await filtersdb.filter(chat_id=chat_id)


async def check_for_filters(chat_id: int, trigger):
    all_filters = await get_all_filters(chat_id)
    for keywords in all_filters:
        keyword = keywords.filter_name
        if trigger == keyword:
            return True
    return False


@Client.on_message(filters.command(["filter", "savefilter"], prefix))
@require_admin(allow_in_private=True)
@use_chat_lang()
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
            m.reply_to_message.caption.markdown
            if m.reply_to_message.caption is not None
            else None
        )
        filter_type = "photo"
    elif m.reply_to_message and m.reply_to_message.document:
        file_id = m.reply_to_message.document.file_id
        raw_data = (
            m.reply_to_message.caption.markdown
            if m.reply_to_message.caption is not None
            else None
        )
        filter_type = "document"
    elif m.reply_to_message and m.reply_to_message.video:
        file_id = m.reply_to_message.video.file_id
        raw_data = (
            m.reply_to_message.caption.markdown
            if m.reply_to_message.caption is not None
            else None
        )
        filter_type = "video"
    elif m.reply_to_message and m.reply_to_message.audio:
        file_id = m.reply_to_message.audio.file_id
        raw_data = (
            m.reply_to_message.caption.markdown
            if m.reply_to_message.caption is not None
            else None
        )
        filter_type = "audio"
    elif m.reply_to_message and m.reply_to_message.animation:
        file_id = m.reply_to_message.animation.file_id
        raw_data = (
            m.reply_to_message.caption.markdown
            if m.reply_to_message.caption is not None
            else None
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
    check_filter = await check_for_filters(chat_id=chat_id, trigger=trigger)
    if check_filter:
        await update_filter(
            chat_id=chat_id,
            trigger=trigger,
            raw_data=raw_data,
            file_id=file_id,
            filter_type=filter_type,
        )
    else:
        await add_filter(
            chat_id=chat_id,
            trigger=trigger,
            raw_data=raw_data,
            file_id=file_id,
            filter_type=filter_type,
        )
    await m.reply_text(
        strings("add_filter_success").format(trigger=trigger), quote=True
    )


@Client.on_message(filters.command(["delfilter", "rmfilter", "stop"], prefix))
@require_admin(allow_in_private=True)
@use_chat_lang()
async def delete_filter(c: Client, m: Message, strings):
    args = m.text.markdown.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    check_filter = await check_for_filters(chat_id=chat_id, trigger=trigger)
    if check_filter:
        await rm_filter(chat_id=chat_id, trigger=trigger)
        await m.reply_text(
            strings("remove_filter_success").format(trigger=trigger), quote=True
        )
    else:
        await m.reply_text(
            strings("no_filter_with_name").format(trigger=trigger), quote=True
        )


@Client.on_message(filters.command("filters", prefix))
@use_chat_lang()
async def get_all_filter(c: Client, m: Message, strings):
    chat_id = m.chat.id
    reply_text = strings("filters_list")
    all_filters = await get_all_filters(chat_id=chat_id)
    for filter_s in all_filters:
        keyword = filter_s.filter_name
        reply_text += f" - {keyword} \n"

    if not all_filters:
        await m.reply_text(strings("filters_list_empty"), quote=True)
    else:
        await m.reply_text(reply_text, quote=True)


@Client.on_message(
    (filters.group | filters.private) & filters.text & filters.incoming, group=1
)
async def serve_filter(c: Client, m: Message):
    chat_id = m.chat.id
    text = m.text
    targeted_message = m.reply_to_message or m

    all_filters = await get_all_filters(chat_id=chat_id)
    for filter_s in all_filters:
        keyword = filter_s.filter_name
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            data, button = button_parser(filter_s.raw_data)
            if filter_s.filter_type == "text":
                await targeted_message.reply_text(
                    data,
                    quote=True,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif filter_s.filter_type == "photo":
                await targeted_message.reply_photo(
                    filter_s.file_id,
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif filter_s.filter_type == "document":
                await targeted_message.reply_document(
                    filter_s.file_id,
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif filter_s.filter_type == "video":
                await targeted_message.reply_video(
                    filter_s.file_id,
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif filter_s.filter_type == "audio":
                await targeted_message.reply_audio(
                    filter_s.file_id,
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif filter_s.filter_type == "animation":
                await targeted_message.reply_animation(
                    filter_s.file_id,
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif filter_s.filter_type == "sticker":
                await targeted_message.reply_sticker(
                    filter_s.file_id,
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )


commands.add_command("delfilter", "admin")
commands.add_command("filter", "admin")
commands.add_command("filters", "general")
