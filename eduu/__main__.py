# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import logging
import sys

import pyrogram
from pyrogram import Client, idle
from pyrogram.errors import BadRequest

import eduu
from eduu.config import API_HASH, API_ID, TOKEN, disabled_plugins, log_chat
from eduu.utils import del_restarted, get_restarted, shell_exec
from eduu.utils.consts import http
from eduu.database import init_database

from tortoise import run_async


client = Client(
    session_name="bot",
    app_version=f"EduuRobot v{eduu.__version__}",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=24,
    parse_mode="html",
    plugins=dict(root="eduu.plugins", exclude=disabled_plugins),
)


async def main() -> None:
    await client.start()
    await init_database()
    # Saving commit number
    client.version_code = int((await shell_exec("git rev-list --count HEAD"))[0])

    client.me = await client.get_me()

    if "test" not in sys.argv:
        wr = await get_restarted()
        await del_restarted()

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

    await http.aclose()
    await client.stop()


run_async(main())
