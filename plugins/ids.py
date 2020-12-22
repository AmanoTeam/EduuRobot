import html

from pyrogram import Client, filters
from pyrogram.types import Message

from localization import use_chat_lang
from config import prefix


@Client.on_message(filters.command("id", prefix) & filters.private)
@use_chat_lang()
async def ids_private(c: Client, m: Message, strings):
    await m.reply_text(strings("info_private").format(
                           first_name=m.from_user.first_name,
                           last_name=m.from_user.last_name or "",
                           username=m.from_user.username,
                           user_id=m.from_user.id,
                           lang=m.from_user.language_code,
                           chat_type=m.chat.type
                       ))


@Client.on_message(filters.command("id", prefix) & filters.group)
@use_chat_lang()
async def ids(c: Client, m: Message, strings):
    data = m.reply_to_message or m
    await m.reply_text(strings("info_group").format(
                           first_name=html.escape(data.from_user.first_name),
                           last_name=html.escape(data.from_user.last_name or ""),
                           username=data.from_user.username,
                           user_id=data.from_user.id,
                           user_dc=data.from_user.dc_id,
                           lang=data.from_user.language_code or strings("unknown_language"),
                           chat_title=m.chat.title,
                           chat_username=m.chat.username,
                           chat_id=m.chat.id,
                           chat_type=m.chat.type,
                           message_id=m.message_id + 1
                       ))
