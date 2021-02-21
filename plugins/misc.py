from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from localization import use_chat_lang
from utils import commands


@Client.on_message(filters.command("mark", prefix))
@use_chat_lang()
async def mark(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("mark_usage"))
    await m.reply(m.text.split(None, 1)[1], parse_mode="markdown")


@Client.on_message(filters.command("html", prefix))
@use_chat_lang()
async def html(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("html_usage"))
    await m.reply(m.text.split(None, 1)[1], parse_mode="html")


commands.add_command("mark", "general")
commands.add_command("html", "general")
