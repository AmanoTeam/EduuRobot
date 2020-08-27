import html

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix


@Client.on_message(filters.command("id", prefix) & filters.private)
async def ids_private(c: Client, m: Message):
    await m.reply_text("<b>Informações:</b>\n\n"
                       "<b>Nome:</b> <code>{first_name} {last_name}</code>\n"
                       "<b>Username:</b> @{username}\n"
                       "<b>ID:</b> <code>{user_id}</code>\n"
                       "<b>Idioma:</b> {lang}\n"
                       "<b>Tipo de chat:</b> {chat_type}".format(
                           first_name=m.from_user.first_name,
                           last_name=m.from_user.last_name or "",
                           username=m.from_user.username,
                           user_id=m.from_user.id,
                           lang=m.from_user.language_code,
                           chat_type=m.chat.type
                       ),
                       parse_mode="HTML")


@Client.on_message(filters.command("id", prefix) & filters.group)
async def ids(c: Client, m: Message):
    data = m.reply_to_message or m
    await m.reply_text("<b>Informações do chat:</b>\n\n"
                       "<b>Nome:</b> <code>{first_name} {last_name}</code>\n"
                       "<b>Username:</b> @{username}\n"
                       "<b>ID:</b> <code>{user_id}</code>\n"
                       "<b>Datacenter:</b> {user_dc}\n"
                       "<b>Idioma:</b> {lang}\n\n"
                       "<b>Nome do chat:</b> <code>{chat_title}</code>\n"
                       "<b>Username do chat:</b> @{chat_username}\n"
                       "<b>ID do chat:</b> <code>{chat_id}</code>\n"
                       "<b>Tipo de chat:</b> {chat_type}".format(
                           first_name=html.escape(data.from_user.first_name),
                           last_name=html.escape(data.from_user.last_name or ""),
                           username=data.from_user.username,
                           user_id=data.from_user.id,
                           user_dc=data.from_user.dc_id,
                           lang=data.from_user.language_code or "-",
                           chat_title=m.chat.title,
                           chat_username=m.chat.username,
                           chat_id=m.chat.id,
                           chat_type=m.chat.type
                       ),
                       parse_mode="HTML")
