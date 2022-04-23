# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import asyncio
import logging
import platform

from httpx import AsyncClient

from eduu.bot import Eduu
from eduu.database import database

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s.%(funcName)s | %(levelname)s | %(message)s",
    datefmt="[%X]",
)

# To avoid some annoying log
logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
logging.getLogger("pyrogram.client").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

try:
    import uvloop

    uvloop.install()
except ImportError:
    if platform.system() != "Windows":
        logger.warning("uvloop is not installed and therefore will be disabled.")


if __name__ == "__main__":
    # open new asyncio event loop
    event_policy = asyncio.get_event_loop_policy()
    event_loop = event_policy.new_event_loop()
    try:
        # start the bot
        event_loop.run_until_complete(database.connect())
        Eduu().run()
    except KeyboardInterrupt:
        # exit gracefully
        logger.warning("Forced stop... Bye!")
    finally:
        # close https connections and the DB if open
        event_loop.run_until_complete(AsyncClient().aclose())
        if database.is_connected:
            event_loop.run_until_complete(database.close())
        # close asyncio event loop
        event_loop.close()
