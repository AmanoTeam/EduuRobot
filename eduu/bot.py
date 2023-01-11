# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import logging
import time

import pyrogram
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import BadRequest
from pyrogram.raw.all import layer

from config import API_HASH, API_ID, DISABLED_PLUGINS, LOG_CHAT, TOKEN, WORKERS

from . import __commit__, __version_number__

logger = logging.getLogger(__name__)


class Eduu(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            name=name,
            app_version=f"EduuRobot r{__version_number__} ({__commit__})",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=TOKEN,
            parse_mode=ParseMode.HTML,
            workers=WORKERS,
            plugins=dict(root="eduu.plugins", exclude=DISABLED_PLUGINS),
            sleep_threshold=180,
        )

    async def start(self):
        await super().start()

        self.start_time = time.time()

        logger.info(
            "Eduu running with Pyrogram v%s (Layer %s) started on @%s. Hi!",
            pyrogram.__version__,
            layer,
            self.me.username,
        )

        from .database.restarted import del_restarted, get_restarted

        wr = await get_restarted()
        await del_restarted()

        start_message = (
            "<b>EduuRobot started!</b>\n\n"
            f"<b>Version number:</b> <code>r{__version_number__} ({__commit__})</code>\n"
            f"<b>Pyrogram:</b> <code>v{pyrogram.__version__}</code>"
        )

        try:
            await self.send_message(chat_id=LOG_CHAT, text=start_message)
            if wr:
                await self.edit_message_text(
                    wr[0], wr[1], text="Restarted successfully!"
                )
        except BadRequest:
            logger.warning("Unable to send message to LOG_CHAT.")

    async def stop(self):
        await super().stop()
        logger.warning("Eduu stopped. Bye!")
