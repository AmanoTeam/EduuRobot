# Copyright (C) 2018-2019 Amano Team <contact@amanoteam.ml>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sqlite3

conn = sqlite3.connect('bot.db')

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS chats (chat_id INTEGER,
                                                    welcome,
                                                    welcome_enabled INTEGER,
                                                    rules,
                                                    goodbye,
                                                    goodbye_enabled INTEGER,
                                                    ia INTEGER,
                                                    warns_limit INTEGER,
                                                    antipedro_enabled INTEGER,
                                                    antipedro_list,
                                                    chat_lang,
                                                    cached_admins)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                                    user_id INTEGER,
                                                    ia INTEGER,
                                                    chat_lang)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
                                                       chat_id INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS was_restarted_on (
                                                               chat_id INTEGER,
                                                               message_id INTEGER)''')


def chat_exists(chat_id):
    cursor.execute('SELECT * FROM chats WHERE chat_id = (?)', (chat_id,))
    if cursor.fetchone():
        return True
    else:
        return False


def channel_exists(chat_id):
    cursor.execute('SELECT * FROM channels WHERE chat_id = (?)', (chat_id,))
    if cursor.fetchone():
        return True
    else:
        return False


def user_exists(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = (?)', (user_id,))
    if cursor.fetchone():
        return True
    else:
        return False


def del_restarted():
    cursor.execute('DELETE FROM was_restarted_on')
    conn.commit()


def add_chat(chat_type, chat_id, chat_lang='en'):
    if chat_type == 'private':
        if not user_exists(chat_id):
            cursor.execute('INSERT INTO users (user_id, chat_lang) VALUES (?,?)', (chat_id, chat_lang))
            conn.commit()
    elif chat_type == 'supergroup' or chat_type == 'group':
        if not chat_exists(chat_id):
            cursor.execute('INSERT INTO chats (chat_id, welcome_enabled, antipedro_list, chat_lang) VALUES (?,?,?,?)',
                           (chat_id, True, '[]', chat_lang))
            conn.commit()
    elif chat_type == 'channel':
        if not channel_exists(chat_id):
            cursor.execute('INSERT INTO channels (chat_id) VALUES (?)', (chat_id,))
            conn.commit()


def get_restarted():
    cursor.execute('SELECT * FROM was_restarted_on')
    return cursor.fetchone()


def set_restarted(chat_id, message_id):
    cursor.execute('INSERT INTO was_restarted_on VALUES (?, ?)', (chat_id, message_id))
    conn.commit()
