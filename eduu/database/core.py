# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import logging

import aiosqlite

from ..config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.conn: aiosqlite.Connection = None
        self.path: str = DATABASE_PATH
        self.is_connected: bool = False

    async def connect(self):
        # Open the connection
        conn = await aiosqlite.connect(self.path)

        # Define the tables
        await conn.executescript(
            """
        CREATE TABLE IF NOT EXISTS groups(
            chat_id INTEGER PRIMARY KEY,
            welcome TEXT,
            welcome_enabled INTEGER,
            rules TEXT,
            warns_limit INTEGER,
            chat_lang TEXT,
            cached_admins,
            antichannelpin INTEGER,
            delservicemsgs INTEGER,
            warn_action TEXT
        );

        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            chat_lang TEXT
        );

        CREATE TABLE IF NOT EXISTS channels(
            chat_id INTEGER PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS was_restarted_at(
            chat_id INTEGER,
            message_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS filters(
            chat_id INTEGER ,
            filter_name TEXT,
            raw_data TEXT,
            file_id TEXT,
            filter_type TEXT
        );

        CREATE TABLE IF NOT EXISTS notes(
            chat_id INTEGER ,
            note_name,
            raw_data,
            file_id,
            note_type
        );

        CREATE TABLE IF NOT EXISTS user_warns(
            user_id INTEGER,
            chat_id INTEGER,
            count INTEGER
        );
        """
        )

        # Enable VACUUM
        await conn.execute("VACUUM")

        # Enable WAL
        await conn.execute("PRAGMA journal_mode=WAL")

        # Update the database
        await conn.commit()

        conn.row_factory = aiosqlite.Row

        self.conn = conn
        self.is_connected: bool = True

        logger.info("The database has been connected.")

    async def close(self):
        # Close the connection
        await self.conn.close()

        self.is_connected: bool = False

        logger.info("The database was closed.")

    def get_conn(self) -> aiosqlite.Connection:
        if not self.is_connected:
            raise RuntimeError("The database is not connected.")

        return self.conn


database = Database()
