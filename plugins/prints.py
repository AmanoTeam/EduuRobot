from io import BytesIO

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from consts import http
from localization import use_chat_lang
from utils import commands


@Client.on_message(filters.command("print", prefix))
@use_chat_lang()
async def prints(_, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("print_usage"), reply_to_message_id=m.message_id
        )
    sent = await m.reply_text(strings("taking_screenshot"))
    text = m.text.split(maxsplit=1)[1]
    r = await http.get("https://webshot.amanoteam.com/print", params=dict(q=text))
    bio = BytesIO(r.read())
    bio.name = "screenshot.png"
    await m.reply_photo(bio)
    await sent.delete()


commands.add_command("print", "tools")
