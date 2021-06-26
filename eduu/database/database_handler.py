# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import sqlite3

db = sqlite3.connect("eduu/database/eduu.db")
dbc = db.cursor()


dbc.execute(
    """CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY,
                                          welcome,
                                          welcome_enabled INTEGER,
                                          rules,
                                          warns_limit INTEGER,
                                          chat_lang,
                                          cached_admins,
                                          antichannelpin,
                                          delservicemsgs,
                                          warn_action)"""
)

dbc.execute(
    """CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,
                                         chat_lang)"""
)

dbc.execute(
    """CREATE TABLE IF NOT EXISTS filters (chat_id INTEGER ,
                                           filter_name,
                                           raw_data,
                                           file_id,
                                           filter_type)"""
)

dbc.execute(
    """CREATE TABLE IF NOT EXISTS notes (chat_id INTEGER ,
                                         note_name,
                                         raw_data,
                                         file_id,
                                         note_type)"""
)

dbc.execute("""CREATE TABLE IF NOT EXISTS channels (chat_id INTEGER PRIMARY KEY)""")

dbc.execute(
    """CREATE TABLE IF NOT EXISTS was_restarted_at (chat_id INTEGER,
                                                    message_id INTEGER)"""
)
dbc.execute(
    """CREATE TABLE IF NOT EXISTS user_warns (user_id INTEGER,
                                              chat_id INTEGER,
                                              count INTEGER)"""
)

db.commit()
