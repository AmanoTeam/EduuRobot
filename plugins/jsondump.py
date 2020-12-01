import json
import html
import io

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix


@Client.on_message(filters.command("jsondump", prefix))
async def jsondump(c: Client, m: Message):
    params = m.text.split()
    send_as_file = len(str(m)) > 3000 or "-f" in params
    # Remove the command and -f flag from list.
    params.pop(0)
    if "-f" in params:
        params.remove("-f")

    # Strip all things like _client and bound methods from Message.
    obj = json.loads(str(m))

    for param in params:
        obj = obj.get(param)
        # There is nothing to get anymore.
        if obj is None:
            break

    obj = json.dumps(obj, indent=4)

    if send_as_file:
        bio = io.BytesIO(obj.encode())
        bio.name = f"dump-{m.chat.id}.json"
        await m.reply_document(bio)
    else:
        await m.reply_text(f"<code>{html.escape(obj)}</code>", parse_mode="HTML")
