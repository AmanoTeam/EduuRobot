
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

from config import bot
import json
import aiml
from db_handler import conn, cursor


k = aiml.Kernel()
k.learn("aiml/antichato.aiml")


def get_antichato(chat_id):
    cursor.execute('SELECT antichato_enabled, antichato_list FROM chats WHERE chat_id = ?', (chat_id,))
    return cursor.fetchall()[0]


def add_user(chat_id, user_id):
    cursor.execute('SELECT antichato_list FROM chats WHERE chat_id = ?', (chat_id,))
    user_list = json.loads(cursor.fetchall()[0][0])
    if user_id not in user_list:
        user_list.append(user_id)
        cursor.execute('UPDATE chats SET antichato_list = ? WHERE chat_id = ?', (json.dumps(user_list), chat_id,))
        conn.commit()
    return True


def remove_user(chat_id, user_id):
    cursor.execute('SELECT antichato_list FROM chats WHERE chat_id = ?', (chat_id,))
    user_list = json.loads(cursor.fetchall()[0][0])
    for num, user in enumerate(user_list):
        if user == user_id:
            del user_list[num]
    cursor.execute('UPDATE chats SET antichato_list = ? WHERE chat_id = ?', (json.dumps(user_list), chat_id,))
    conn.commit()


def antichato(msg):
    if msg.get('chat') and msg.get('from') and msg['chat']['type'].endswith('group'):
        ac = get_antichato(msg['chat']['id'])
        if ac[0] and msg['from']['id'] in json.loads(ac[1]):
            bot.sendMessage(msg['chat']['id'], k.respond('a'), reply_to_message_id=msg['message_id'])