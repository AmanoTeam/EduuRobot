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

from config import bot, bot_username

from db_handler import conn, cursor
from .admins import is_admin


def get_rules(chat_id):
    cursor.execute('SELECT rules FROM chats WHERE chat_id = (?)', (chat_id,))
    try:
        return cursor.fetchone()[0]
    except IndexError:
        return None


def set_rules(chat_id, rules):
    cursor.execute('UPDATE chats SET rules = ? WHERE chat_id = ?', (rules, chat_id))
    conn.commit()


async def rules(msg):
    if msg.get('text'):

        if msg['text'].startswith('/start rules_'):
            chat_id = msg['text'].split('_')[1]
            rules = get_rules(int(chat_id)) or 'Sem regras!'

            await bot.sendMessage(msg['chat']['id'], rules, 'Markdown')
            return True


        elif msg['text'] == '/rules' or msg['text'] == '!rules' or msg['text'] == '/regras' or msg[
            'text'] == '!regras' or msg['text'] == '/regras@' + bot_username or msg['text'] == '/rules@' + bot_username:
            rules = get_rules(msg['chat']['id']) or 'Sem regras!'

            await bot.sendMessage(msg['chat']['id'], rules, 'Markdown',
                                  reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].split()[0] == '/defrules' or msg['text'].split()[0] == '!defrules' or msg['text'].split()[
            0] == '/defregras' or msg['text'].split()[0] == '!defregras' or msg['text'].split()[
            0] == '/defregras@' + bot_username or msg['text'].split()[0] == '/defrules@' + bot_username:
            if (await is_admin(msg['chat']['id'], msg['from']['id']))['user']:
                if len(msg['text'].split()) == 1:
                    await bot.sendMessage(msg['chat']['id'], 'Uso: /defregras Regras do grupo (suporta Markdown)',
                                          reply_to_message_id=msg['message_id'])
                elif msg['text'].split()[1] == 'reset':
                    set_rules(msg['chat']['id'], None)
                    await bot.sendMessage(msg['chat']['id'], 'As regras do grupo foram redefinidas com sucesso.',
                                          reply_to_message_id=msg['message_id'])
                else:
                    set_rules(msg['chat']['id'], msg['text'].split(' ', 1)[1])
                    await bot.sendMessage(msg['chat']['id'], 'As regras do grupo foram definidas com sucesso.',
                                          reply_to_message_id=msg['message_id'])
            return True
