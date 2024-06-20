# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

import re

from hydrogram import Client, filters
from hydrogram.enums import ParseMode
from hydrogram.types import InlineKeyboardMarkup, Message

from config import PREFIXES
from eduu.database.notes import add_note, get_all_notes, rm_note, update_note
from eduu.utils import button_parser, commands, split_quotes
from eduu.utils.decorators import require_admin
from eduu.utils.localization import Strings, use_chat_lang


async def check_for_notes(chat_id, trigger):
    all_notes = await get_all_notes(chat_id)
    for keywords in all_notes:
        keyword = keywords[1]
        if trigger == keyword:
            return True
    return False


@Client.on_message(filters.command(["note", "savenote", "nota", "salvarnota"], PREFIXES))
@require_admin(allow_in_private=True)
@use_chat_lang
async def save_note(c: Client, m: Message, s: Strings):
    args = m.text.html.split(maxsplit=1)
    split_text = split_quotes(args[1])
    trigger = split_text[0].lower()

    if m.reply_to_message is None and len(split_text) < 2:
        await m.reply_text(s("notes_add_empty"), quote=True)
        return

    if m.reply_to_message.media and m.reply_to_message.media.value in (
        "photo", "document", "video", "audio", "animation"
    ):
        file_id = getattr(m.reply_to_message, m.reply_to_message.media.value).file_id
        raw_data = (
            m.reply_to_message.caption.html if m.reply_to_message.caption is not None else None
        )
        note_type = m.reply_to_message.media.value
    elif m.reply_to_message and m.reply_to_message.sticker:
        file_id = m.reply_to_message.sticker.file_id
        raw_data = split_text[1] if len(split_text) > 1 else None
        note_type = "sticker"
    else:
        file_id = None
        raw_data = split_text[1]
        note_type = "text"

    chat_id = m.chat.id
    check_note = await check_for_notes(chat_id, trigger)
    if check_note:
        await update_note(chat_id, trigger, raw_data, file_id, note_type)
    else:
        await add_note(chat_id, trigger, raw_data, file_id, note_type)
    await m.reply_text(s("notes_add_success").format(trigger=trigger), quote=True)


@Client.on_message(filters.command(["delnote", "rmnote", "delnota", "rmnota"], PREFIXES))
@require_admin(allow_in_private=True)
@use_chat_lang
async def delete_note(c: Client, m: Message, s: Strings):
    args = m.text.html.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    check_note = await check_for_notes(chat_id, trigger)
    if check_note:
        await rm_note(chat_id, trigger)
        await m.reply_text(s("notes_remove_success").format(trigger=trigger), quote=True)
    else:
        await m.reply_text(s("notes_no_note_with_name").format(trigger=trigger), quote=True)


@Client.on_message(filters.command(["notes", "notas"], PREFIXES))
@use_chat_lang
async def get_all_chat_note(c: Client, m: Message, s: Strings):
    chat_id = m.chat.id
    reply_text = s("notes_list")
    all_notes = await get_all_notes(chat_id)
    for note_s in all_notes:
        keyword = note_s[1]
        reply_text += f" - {keyword} \n"

    if not all_notes:
        await m.reply_text(s("notes_list_empty"), quote=True)
    else:
        await m.reply_text(reply_text, quote=True)


async def serve_note(c: Client, m: Message, txt):
    chat_id = m.chat.id
    text = txt

    all_notes = await get_all_notes(chat_id)
    for note in all_notes:
        keyword = note[1]
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if not re.search(pattern, text, flags=re.IGNORECASE):
            continue

        data, button = button_parser(note[2])
        if note[4] == "text":
            await m.reply_text(
                data,
                quote=True,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )
        elif note[4] in ("photo", "document", "video", "audio", "animation", "sticker"):
            await m.reply_cached_media(
                note[3],
                quote=True,
                caption=data,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(button) if len(button) != 0 else None,
            )

@Client.on_message(
    (filters.group | filters.private)
    & filters.text
    & filters.incoming
    & filters.regex(r"^#[^\s]+"),
    group=2,
)
async def note_by_hashtag(c: Client, m: Message):
    note_data = m.text[1:]
    targeted_message = m.reply_to_message or m
    await serve_note(c, targeted_message, txt=note_data)


@Client.on_message(
    (filters.group | filters.private)
    & filters.text
    & filters.incoming
    & filters.command("get", PREFIXES),
    group=2,
)
async def note_by_get_command(c: Client, m: Message):
    note_data = " ".join(m.command[1:])
    targeted_message = m.reply_to_message or m
    await serve_note(c, targeted_message, txt=note_data)


commands.add_command("delnote", "admin")
commands.add_command("note", "admin")
commands.add_command("notes", "general")
