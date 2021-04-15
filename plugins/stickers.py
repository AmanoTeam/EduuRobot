from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from localization import use_chat_lang
import os


@Client.on_message(filters.command("stickerid", prefix) & filters.reply)
@use_chat_lang()
async def getstickerid(c: Client, m: Message, strings):
    if m.reply_to_message.sticker:
        await m.reply_text(strings("get_sticker_id_string").format(stickerid=m.reply_to_message.sticker.file_id))


@Client.on_message(filters.command("getsticker", prefix) & filters.reply)
@use_chat_lang()
async def getstickeraspng(c: Client, m: Message, strings):
    if m.reply_to_message.sticker:
        if m.reply_to_message.sticker.is_animated:
            await m.reply_text(strings("animated_not_supported"))
        if not m.reply_to_message.sticker.is_animated:
            thesticker = await m.reply_to_message.download(file_name="sticker.png")
            await m.reply_to_message.reply_photo(thesticker)
            os.remove(thesticker)
