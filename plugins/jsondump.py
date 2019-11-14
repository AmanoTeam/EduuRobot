import html
import os

from pyrogram import Client, Filters

from config import prefix


@Client.on_message(Filters.command("jsondump", prefix))
async def jsondump(client, message):
    if len(str(message)) < 3000 and "-f" not in message.command:
        await message.reply_text(f"<code>{html.escape(str(message))}</code>", parse_mode="HTML")
    else:
        fname = f"dump-{message.chat.id}.json"
        with open(fname, "w") as f:
            f.write(str(message))
        await message.reply_document(fname)
        os.remove(fname)
