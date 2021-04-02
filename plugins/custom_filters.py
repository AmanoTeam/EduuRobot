import re

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from config import prefix
from localization import use_chat_lang
from utils import require_admin, split_quotes, button_parser
from dbh import dbc, db


def add_filter(chat_id, trigger, raw_data, file_id):
    dbc.execute(
        "INSERT INTO filters(chat_id, filter_name, raw_data, file_id) VALUES(?, ?, ?, ?)",
        (chat_id, trigger, raw_data, file_id)
    )
    db.commit()


def update_filter(chat_id, trigger, raw_data, file_id):
    dbc.execute(
        "UPDATE filters SET raw_data = ?, file_id = ? WHERE chat_id = ? AND filter_name = ?",
        (chat_id, trigger, raw_data, file_id)
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


@Client.on_message(filters.command("filter", prefixes=prefix))
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

    file_id = None
    raw_data = split_text[1]

    chat_id = m.chat.id
    check_filter = check_for_filters(chat_id, trigger)
    if check_filter:
        update_filter(chat_id, trigger, raw_data, file_id)
    else:
        add_filter(chat_id, trigger, raw_data, file_id)
    await m.reply_text(
        f"Added filter **{trigger}**",
        quote=True,
        parse_mode="md"
    )


@Client.on_message(filters.command(["delfilter", "rmfilter"], prefixes=prefix))
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


@Client.on_message(filters.group & filters.text & filters.incoming, group=1)
async def serve_filter(c: Client, m: Message):
    chat_id = m.chat.id
    text = m.text

    all_filters = get_all_filters(chat_id)
    for filter_s in all_filters:
        keyword = filter_s[1]
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            data, button = button_parser(filter_s[2])
            await m.reply_text(
                data,
                quote=True,
                parse_mode="md",
                reply_markup=InlineKeyboardMarkup(
                    button
                ) if len(button) != 0 else None
            )
