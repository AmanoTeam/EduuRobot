import html
import os

from pyrogram import Client, Filters, Message

from config import prefix


@Client.on_message(Filters.command("jsondump", prefix))
async def jsondump(c: Client, m: Message):
    if len(str(m)) < 3000 and "-f" not in m.command:
        await m.reply_text(f"<code>{html.escape(str(m))}</code>", parse_mode="HTML")
    else:
        fname = f"dump-{m.chat.id}.json"
        with open(fname, "w") as f:
            f.write(str(m))
        await m.reply_document(fname)
        os.remove(fname)
