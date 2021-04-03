import re

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from config import prefix
from localization import use_chat_lang
from utils import require_admin, split_quotes, button_parser
from dbh import dbc, db


def add_filter(chat_id, trigger, raw_data, file_id, filter_type):
    dbc.execute(
        "INSERT INTO filters(chat_id, filter_name, raw_data, file_id, filter_type) VALUES(?, ?, ?, ?, ?)",
        (chat_id, trigger, raw_data, file_id, filter_type),
    )
    db.commit()


def update_filter(chat_id, trigger, raw_data, file_id, filter_type):
    dbc.execute(
        "UPDATE filters SET raw_data = ?, file_id = ?, filter_type = ? WHERE chat_id = ? AND filter_name = ?",
        (raw_data, file_id, filter_type, chat_id, trigger),
    )
    db.commit()


def rm_filter(chat_id, trigger):
    dbc.execute(
        "DELETE from filters WHERE chat_id = ? AND filter_name = ?",
        (chat_id, trigger)
    )
    db.commit()


def get_all_filters(chat_id):
    dbc.execute(
        "SELECT * FROM filters WHERE chat_id = ?",
        (chat_id,)
    )

    db.commit()
    return dbc.fetchall()


def check_for_filters(chat_id, trigger):
    all_filters = get_all_filters(chat_id)
    for keywords in all_filters:
        keyword = keywords[1]
        if trigger == keyword:
            return True
    return False


@Client.on_message(filters.command(["filter", "savefilter"], prefix))
@require_admin(allow_in_private=True)
async def save_filter(c: Client, m: Message):
    args = m.text.markdown.split(maxsplit=1)
    split_text = split_quotes(args[1])
    trigger = split_text[0].lower()

    if m.reply_to_message is None and len(split_text) < 2:
        await m.reply_text(
            "There is no content in the filter",
            quote=True
        )
        return

    if m.reply_to_message and m.reply_to_message.photo:
        file_id = m.reply_to_message.photo.file_id
        raw_data = m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        filter_type = "photo"
    elif m.reply_to_message and m.reply_to_message.document:
        file_id = m.reply_to_message.document.file_id
        raw_data = m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        filter_type = "document"
    elif m.reply_to_message and m.reply_to_message.video:
        file_id = m.reply_to_message.video.file_id
        raw_data = m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        filter_type = "video"
    elif m.reply_to_message and m.reply_to_message.audio:
        file_id = m.reply_to_message.audio.file_id
        raw_data = m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        filter_type = "audio"
    elif m.reply_to_message and m.reply_to_message.animation:
        file_id = m.reply_to_message.animation.file_id
        raw_data = m.reply_to_message.caption.markdown if m.reply_to_message.caption is not None else None
        filter_type = "animation"
    elif m.reply_to_message and m.reply_to_message.sticker:
        file_id = m.reply_to_message.sticker.file_id
        raw_data = split_text[1]
        filter_type = "sticker"
    else:
        file_id = None
        raw_data = split_text[1]
        filter_type = "text"

    chat_id = m.chat.id
    check_filter = check_for_filters(chat_id, trigger)
    if check_filter:
        update_filter(chat_id, trigger, raw_data, file_id, filter_type)
    else:
        add_filter(chat_id, trigger, raw_data, file_id, filter_type)
    await m.reply_text(
        f"Added filter **{trigger}**",
        quote=True,
        parse_mode="md"
    )


@Client.on_message(filters.command(["delfilter", "rmfilter", "stop"], prefix))
@require_admin(allow_in_private=True)
async def delete_filter(c: Client, m: Message):
    args = m.text.markdown.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    check_filter = check_for_filters(chat_id, trigger)
    if check_filter:
        rm_filter(chat_id, trigger)
        await m.reply_text(
            f"Removed **{trigger}** from filters",
            quote=True,
            parse_mode="md"
        )
    else:
        await m.reply_text(
            f"There is no filter with name **{trigger}**",
            quote=True,
            parse_mode="md"
        )


@Client.on_message(filters.command("filters", prefix))
async def get_all_filter(c: Client, m: Message):
    chat_id = m.chat.id
    reply_text = "Filters in this chat\n\n"
    all_filters = get_all_filters(chat_id)
    for filter_s in all_filters:
        keyword = filter_s[1]
        reply_text += f" - {keyword} \n"

    if reply_text == "Filters in this chat\n\n":
        await m.reply_text(
            "Currently no filters in the chat",
            quote=True
        )
    else:
        await m.reply_text(
            reply_text,
            quote=True
        )


@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming, group=1)
async def serve_filter(c: Client, m: Message):
    chat_id = m.chat.id
    text = m.text

    all_filters = get_all_filters(chat_id)
    for filter_s in all_filters:
        keyword = filter_s[1]
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            data, button = button_parser(filter_s[2])
            if filter_s[4] == "text":
                await m.reply_text(
                    data,
                    quote=True,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ) if len(button) != 0 else None
                )
            elif filter_s[4] == "photo":
                await m.reply_photo(
                    filter_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ) if len(button) != 0 else None
                )
            elif filter_s[4] == "document":
                await m.reply_document(
                    filter_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ) if len(button) != 0 else None
                )
            elif filter_s[4] == "video":
                await m.reply_video(
                    filter_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ) if len(button) != 0 else None
                )
            elif filter_s[4] == "audio":
                await m.reply_audio(
                    filter_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ) if len(button) != 0 else None
                )
            elif filter_s[4] == "animation":
                await m.reply_animation(
                    filter_s[3],
                    quote=True,
                    caption=data if not None else None,
                    parse_mode="md",
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ) if len(button) != 0 else None
                )
            elif filter_s[4] == "sticker":
                await m.reply_sticker(
                    filter_s[3],
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ) if len(button) != 0 else None
                )
