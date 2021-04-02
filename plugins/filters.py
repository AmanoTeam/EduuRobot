from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from localization import use_chat_lang
from utils import require_admin, split_quotes, button_parser
from dbh import dbc, db


def add_filter(chat_id, trigger, text, button, file_id):
    dbc.execute(
        "INSERT INTO filters(chat_id, filter_name, text, button, file) VALUES(?, ?, ?, ?, ?)",
        (chat_id, trigger, text, button, file_id)
    )
    db.commit()


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
    if m.reply_to_message:
        message = m.reply_to_message.photo or \
            m.reply_to_message.video or \
            m.reply_to_message.video_note or \
            m.reply_to_message.document or \
            m.reply_to_message.animation or \
            m.reply_to_message.sticker

        if message and m.reply_to_message.caption is not None:
            file_id = message.file_id
            if m.reply_to_message.reply_markup:
                button = m.reply_to_message.reply_markup.inline_keyboard
                text = m.reply_to_message.caption.markdown
            else:
                text, button = button_parser(m.reply_to_message.caption.markdown)

        else:
            file_id = message.file_id
            text, button = button_parser(split_text[1])
    else:
        file_id = None
        text, button = button_parser(split_text[1])

    chat_id = m.chat.id
    add_filter(chat_id, trigger, text, button, file_id)
    await m.reply_text(
        f"Added filter **{trigger}**",
        quote=True,
        parse_mode="md"
    )
