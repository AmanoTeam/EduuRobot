from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from consts import http
from utils import commands


@Client.on_message(filters.command("print", prefix))
async def prints(c: Client, m: Message):
    if len(m.command) == 1:
        return await m.reply_text(
            "Please specify a url", reply_to_message_id=m.message_id
        )
    sent = await m.reply_text("Taking a screenshot...")
    text = m.text.split(maxsplit=1)[1]
    r = await http.get("https://amn-api.herokuapp.com/print", params=dict(q=text))
    bio = BytesIO(r.read())
    bio.name = "screenshot.png"
    await m.reply_photo(bio)
    await sent.delete()


commands.add_command("print", "tools")
