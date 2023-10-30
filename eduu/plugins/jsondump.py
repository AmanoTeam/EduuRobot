# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import html
import io
import json

from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from eduu.utils import commands


@Client.on_message(filters.command("jsondump", PREFIXES))
async def jsondump(c: Client, m: Message):
    params = m.text.split()
    # Remove the command name.
    params.pop(0)

    # Strip all things like _client and bound methods from Message.
    obj = json.loads(str(m))

    force_file = False
    # Remove the -f flag from list if present and set force_file to True.
    if "-f" in params:
        force_file = True
        params.remove("-f")

    for param in params:
        param = int(param) if param.lstrip("-").isdecimal() else param
        try:
            obj = obj[param]
        except (IndexError, KeyError) as e:
            return await m.reply_text(f"{e.__class__.__name__}: {e}")
        # There is nothing to get anymore.
        if obj is None:
            break

    obj = json.dumps(obj, indent=4, ensure_ascii=False)

    as_file = force_file or len(obj) > 3000

    if as_file:
        bio = io.BytesIO(obj.encode())
        bio.name = f"dump-{m.chat.id}.json"
        await m.reply_document(bio)
        return None
    else:
        await m.reply_text(f"<code>{html.escape(obj)}</code>")
        return None


commands.add_command("jsondump", "tools")
