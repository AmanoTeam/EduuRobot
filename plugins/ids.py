import html
from config import prefix
from pyrogram import Client, Filters


@Client.on_message(Filters.command("id", prefix) & Filters.private)
async def ids_private(client, message):
    await message.reply_text("<b>Informações:</b>\n\n"
                             "<b>Nome:</b> <code>{first_name} {last_name}</code>\n"
                             "<b>Username:</b> @{username}\n"
                             "<b>ID:</b> <code>{user_id}</code>\n"
                             "<b>Idioma:</b> {lang}\n"
                             "<b>Tipo de chat:</b> {chat_type}".format(
                                 first_name=message.from_user.first_name,
                                 last_name=message.from_user.last_name or "",
                                 username=message.from_user.username,
                                 user_id=message.from_user.id,
                                 lang=message.from_user.language_code,
                                 chat_type=message.chat.type
                             ),
                             parse_mode="HTML")


@Client.on_message(Filters.command("id", prefix) & Filters.group)
async def ids(client, message):
    data = message.reply_to_message or message
    await message.reply_text("<b>Informações do chat:</b>\n\n"
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
                                 chat_title=message.chat.title,
                                 chat_username=message.chat.username,
                                 chat_id=message.chat.id,
                                 chat_type=message.chat.type
                             ),
                             parse_mode="HTML")
