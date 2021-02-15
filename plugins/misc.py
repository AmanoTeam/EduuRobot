from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from utils import commands

@Client.on_message(filters.command("mark", prefix))
async def echo(c: Client, m: Message):
 await m.reply(m.text.split(None, 1)[1], parse_mode="markdown")


@Client.on_message(filters.command("html", prefix))
async def echo(c: Client, m: Message):
 await m.reply(m.text.split(None, 1)[1], parse_mode="html")
 
commands.add_command("mark", "general")
commands.add_command("html", "general")
