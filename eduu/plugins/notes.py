# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import re

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, Message

from eduu.config import prefix
from eduu.database import db, dbc
from eduu.utils import button_parser, commands, require_admin, split_quotes
from eduu.utils.localization import use_chat_lang


dbc.execute(
    """CREATE TABLE IF NOT EXISTS notes (chat_id INTEGER ,
                                         note_name,
                                         raw_data,
                                         file_id,
                                         note_type)"""
)


def add_note(chat_id, trigger, raw_data, file_id, note_type):
    dbc.execute(
        "INSERT INTO notes(chat_id, note_name, raw_data, file_id, note_type) VALUES(?, ?, ?, ?, ?)",
        (chat_id, trigger, raw_data, file_id, note_type),
    )
    db.commit()


def update_note(chat_id, trigger, raw_data, file_id, note_type):
    dbc.execute(
        "UPDATE notes SET raw_data = ?, file_id = ?, note_type = ? WHERE chat_id = ? AND note_name = ?",
        (raw_data, file_id, note_type, chat_id, trigger),
    )
    db.commit()


def rm_note(chat_id, trigger):
    dbc.execute(
        "DELETE from notes WHERE chat_id = ? AND note_name = ?", (chat_id, trigger)
    )
    db.commit()


def get_all_notes(chat_id):
    dbc.execute("SELECT * FROM notes WHERE chat_id = ?", (chat_id,))

    return dbc.fetchall()


def check_for_notes(chat_id, trigger):
    all_notes = get_all_notes(chat_id)
    for keywords in all_notes:
        keyword = keywords[1]
        if trigger == keyword:
            return True
    return False


@Client.on_message(filters.command(["note", "savenote"], prefix))
@require_admin(allow_in_private=True)
@use_chat_lang()
async def save_note(c: Client, m: Message, strings):
    args = m.text.html.split(maxsplit=1)
    split_text = split_quotes(args[1])
    trigger = split_text[0].lower()

    if m.reply_to_message is None and len(split_text) < 2:
        await m.reply_text(strings("add_note_empty"), quote=True)
        return

    if m.reply_to_message and m.reply_to_message.photo:
        file_id = m.reply_to_message.photo.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "photo"
    elif m.reply_to_message and m.reply_to_message.document:
        file_id = m.reply_to_message.document.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "document"
    elif m.reply_to_message and m.reply_to_message.video:
        file_id = m.reply_to_message.video.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "video"
    elif m.reply_to_message and m.reply_to_message.audio:
        file_id = m.reply_to_message.audio.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "audio"
    elif m.reply_to_message and m.reply_to_message.animation:
        file_id = m.reply_to_message.animation.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "animation"
    elif m.reply_to_message and m.reply_to_message.sticker:
        file_id = m.reply_to_message.sticker.file_id
        raw_data = split_text[1] if len(split_text) > 1 else None
        note_type = "sticker"
    else:
        file_id = None
        raw_data = split_text[1]
        note_type = "text"

    chat_id = m.chat.id
    check_note = check_for_notes(chat_id, trigger)
    if check_note:
        update_note(chat_id, trigger, raw_data, file_id, note_type)
    else:
        add_note(chat_id, trigger, raw_data, file_id, note_type)
    await m.reply_text(strings("add_note_success").format(trigger=trigger), quote=True)


@Client.on_message(filters.command(["delnote", "rmnote"], prefix))
@require_admin(allow_in_private=True)
@use_chat_lang()
async def delete_note(c: Client, m: Message, strings):
    args = m.text.html.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    check_note = check_for_notes(chat_id, trigger)
    if check_note:
        rm_note(chat_id, trigger)
        await m.reply_text(
            strings("remove_note_success").format(trigger=trigger), quote=True
        )
    else:
        await m.reply_text(
            strings("no_note_with_name").format(trigger=trigger), quote=True
        )


@Client.on_message(filters.command("notes", prefix))
@use_chat_lang()
async def get_all_chat_note(c: Client, m: Message, strings):
    chat_id = m.chat.id
    reply_text = strings("notes_list")
    all_notes = get_all_notes(chat_id)
    for note_s in all_notes:
        keyword = note_s[1]
        reply_text += f" - {keyword} \n"

    if not all_notes:
        await m.reply_text(strings("notes_list_empty"), quote=True)
    else:
        await m.reply_text(reply_text, quote=True)


async def serve_note(c: Client, m: Message, txt):
    chat_id = m.chat.id
    text = txt

    all_notes = get_all_notes(chat_id)
    for note_s in all_notes:
        keyword = note_s[1]
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            data, button = button_parser(note_s[2])
            if note_s[4] == "text":
                await m.reply_text(
                    data,
                    quote=True,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s[4] == "photo":
                await m.reply_photo(
                    note_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s[4] == "document":
                await m.reply_document(
                    note_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s[4] == "video":
                await m.reply_video(
                    note_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s[4] == "audio":
                await m.reply_audio(
                    note_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s[4] == "animation":
                await m.reply_animation(
                    note_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s[4] == "sticker":
                await m.reply_sticker(
                    note_s[3],
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
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
    & filters.command("get", prefix),
    group=2,
)
async def note_by_get_command(c: Client, m: Message):
    note_data = " ".join(m.command[1:])
    targeted_message = m.reply_to_message or m
    await serve_note(c, targeted_message, txt=note_data)


commands.add_command("delnote", "admin")
commands.add_command("note", "admin")
commands.add_command("notes", "general")
