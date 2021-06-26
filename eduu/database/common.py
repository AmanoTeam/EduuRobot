# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import sqlite3

db = sqlite3.connect("eduu/database/eduu.db")
dbc = db.cursor()


dbc.executescript(
    """
CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY,
                                   welcome,
                                   welcome_enabled INTEGER,
                                   rules,
                                   warns_limit INTEGER,
                                   chat_lang,
                                   cached_admins,
                                   antichannelpin,
                                   delservicemsgs,
                                   warn_action);

CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,
                                  chat_lang);

CREATE TABLE IF NOT EXISTS channels (chat_id INTEGER PRIMARY KEY);

CREATE TABLE IF NOT EXISTS was_restarted_at (chat_id INTEGER,
                                             message_id INTEGER);
"""
)


db.commit()
