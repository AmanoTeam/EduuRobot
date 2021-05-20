from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.utils import commands


@Client.on_message(filters.command("ping", prefix))
async def ping(c: Client, m: Message):
    first = datetime.now()
    sent = await m.reply_text("<b>Pong!</b>")
    second = datetime.now()
    await sent.edit_text(
        f"<b>Pong!</b> <code>{(second - first).microseconds / 1000}</code>ms"
    )


commands.add_command("ping", "general")
