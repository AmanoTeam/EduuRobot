import asyncio
import logging
import sys

from pyrogram import Client, idle
from pyrogram.errors import BadRequest

from config import API_HASH, API_ID, TOKEN, disabled_plugins, log_chat
from consts import http
from utils import del_restarted, get_restarted

with open("version.txt") as f:
    version = f.read().strip()


client = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=24,
    parse_mode="html",
    plugins=dict(root="plugins", exclude=disabled_plugins),
)


async def main():
    await client.start()

    if "test" not in sys.argv:
        wr = get_restarted()
        del_restarted()
        try:
            await client.send_message(
                log_chat,
                f"<b>Bot started</b>\n\n<b>Version:</b> <code>{version}</code>",
            )
            if wr:
                await client.edit_message_text(wr[0], wr[1], "Restarted successfully!")
        except BadRequest:
            logging.warning("Unable to send message to log_chat.")
            pass
        await idle()

    await http.aclose()
    await client.stop()


loop = asyncio.get_event_loop()

loop.run_until_complete(main())
