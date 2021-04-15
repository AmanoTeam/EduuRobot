from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from localization import use_chat_lang


@Client.on_message(filters.command("stickerid", prefix) & filters.reply)
@use_chat_lang()
async def getstickerid(c: Client, m: Message, strings):
    if m.reply_to_message.sticker:
        stickerid = m.reply_to_message.sticker.file_id
        await m.reply_text(strings("sticker_id_strings").format(stickerid=stickerid))
