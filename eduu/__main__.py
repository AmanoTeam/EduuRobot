import asyncio
import logging
import sys

import pyrogram
from pyrogram import Client, idle
from pyrogram.errors import BadRequest

from eduu.config import API_HASH, API_ID, TOKEN, disabled_plugins, log_chat
from eduu.utils import del_restarted, get_restarted
from eduu.utils.consts import http

with open("./eduu/version.txt") as f:
    version = f.read().strip()


client = Client(
    session_name="bot",
    app_version=f"EduuRobot {version}",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=24,
    parse_mode="html",
    plugins=dict(root="eduu.plugins", exclude=disabled_plugins),
)


async def main():
    await client.start()

    if "test" not in sys.argv:
        wr = get_restarted()
        del_restarted()

        start_message = (
            "<b>EduuRobot started!</b>\n\n"
            f"<b>Version:</b> <code>{version}</code>\n"
            f"<b>Pyrogram:</b> <code>v{pyrogram.__version__}</code>"
        )

        try:
            await client.send_message(chat_id=log_chat, text=start_message)
            if wr:
                await client.edit_message_text(wr[0], wr[1], "Restarted successfully!")
        except BadRequest:
            logging.warning("Unable to send message to log_chat.")

        await idle()

    await http.aclose()
    await client.stop()


loop = asyncio.get_event_loop()

loop.run_until_complete(main())
