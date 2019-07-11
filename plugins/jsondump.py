import html
from config import prefix
from pyrogram import Client, Filters


@Client.on_message(Filters.command("jsondump", prefix))
async def start_private(client, message):
    await message.reply(f"<code>{html.escape(str(message))}</code>", parse_mode="HTML")
