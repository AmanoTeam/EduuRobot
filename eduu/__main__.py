# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import asyncio
import logging
import platform
import sys
import time

import pyrogram
from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from pyrogram.errors import BadRequest

import eduu
from eduu.config import API_HASH, API_ID, TOKEN, disabled_plugins, log_chat
from eduu.utils import del_restarted, get_restarted, shell_exec

try:
    import uvloop

    uvloop.install()
except ImportError:
    if platform.system() != "Windows":
        logging.warning("uvloop is not installed and therefore will be disabled.")


async def main() -> None:
    client = Client(
        name="bot",
        app_version=f"EduuRobot v{eduu.__version__}",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=TOKEN,
        workers=24,
        parse_mode=ParseMode.HTML,
        plugins=dict(root="eduu.plugins", exclude=disabled_plugins),
    )

    await client.start()

    # Saving commit number
    client.version_code = int((await shell_exec("git rev-list --count HEAD"))[0])

    client.me = await client.get_me()

    client.start_time = time.time()
    if "test" not in sys.argv:
        wr = get_restarted()
        del_restarted()

        start_message = (
            "<b>EduuRobot started!</b>\n\n"
            f"<b>Version:</b> <code>v{eduu.__version__} ({client.version_code})</code>\n"
            f"<b>Pyrogram:</b> <code>v{pyrogram.__version__}</code>"
        )

        try:
            await client.send_message(chat_id=log_chat, text=start_message)
            if wr:
                await client.edit_message_text(wr[0], wr[1], "Restarted successfully!")
        except BadRequest:
            logging.warning("Unable to send message to log_chat.")

        await idle()

    await client.stop()


event_policy = asyncio.get_event_loop_policy()
event_loop = event_policy.new_event_loop()
event_loop.run_until_complete(main())
