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

import time

from db_handler import conn, cursor
from .admins import is_admin
from config import bot

cursor.execute('CREATE TABLE IF NOT EXISTS antiflood (chat_id, user_id, unix_time)')


async def antiflood(msg):
    if msg.get('chat') and msg['chat']['type'].endswith('group') and msg.get('from'):
        adm = await is_admin(msg['chat']['id'], msg['from']['id'])
        if not adm['user'] and adm['bot']:
            # Delete old rows.
            cursor.execute('DELETE FROM antiflood WHERE chat_id = ? AND unix_time < ?',
                           (msg['chat']['id'], int(time.time()) - 5))
            conn.commit()

            # Insert antiflood row.
            cursor.execute('INSERT INTO antiflood (chat_id, user_id, unix_time) VALUES (?,?,?)',
                           (msg['chat']['id'], msg['from']['id'], int(time.time())))
            conn.commit()

            # Get total rows count.
            cursor.execute('SELECT COUNT(*) FROM antiflood WHERE chat_id = ? AND user_id = ?',
                           (msg['chat']['id'], msg['from']['id']))
            msgs = cursor.fetchone()[0]

            if msgs == 5:
                await bot.sendMessage(msg['chat']['id'], 'Flood!')
                return True
