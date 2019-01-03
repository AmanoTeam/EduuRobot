from config import bot, bot_username, bot_id
from db_handler import conn, cursor
from .admins import is_admin


def get_rules(chat_id):
    cursor.execute('SELECT rules FROM chats WHERE chat_id = (?)', (chat_id,))
    try:
        return cursor.fetchall()[0]
    except IndexError:
        return None


def set_rules(chat_id, rules):
    cursor.execute('UPDATE chats SET rules = ? WHERE chat_id = ?', (rules, chat_id))
    conn.commit()


def rules(msg):
    if msg.get('text'):

        if msg['text'].startswith('/start rules_'):
            chat_id = msg['text'].split('_')[1]
            rules = get_rules(int(chat_id))[0] or 'Sem regras!'

            bot.sendMessage(msg['chat']['id'], rules, 'Markdown')


        elif msg['text'] == '/rules' or msg['text'] == '!rules' or msg['text'] == '/regras' or msg['text'] == '!regras' or msg['text'] == '/regras@'+bot_username or msg['text'] == '/rules@'+bot_username:
            rules = get_rules(msg['chat']['id'])[0] or 'Sem regras!'

            bot.sendMessage(msg['chat']['id'], rules, 'Markdown',
                            reply_to_message_id=msg['message_id'])


        elif msg['text'].split()[0] == '/defrules' or msg['text'].split()[0] == '!defrules' or msg['text'].split()[0] == '/defregras' or msg['text'].split()[0] == '!defregras' or msg['text'].split()[0] == '/defregras@'+bot_username or msg['text'].split()[0] == '/defrules@'+bot_username:
            if is_admin(msg['chat']['id'], msg['from']['id'])['user']:
                if len(msg['text'].split()) == 1:
                    bot.sendMessage(msg['chat']['id'], 'Uso: /defregras Regras do grupo (suporta Markdown)',
                                    reply_to_message_id=msg['message_id'])
                elif msg['text'].split()[1] == 'reset':
                    set_rules(msg['chat']['id'], None)
                    bot.sendMessage(msg['chat']['id'], 'As regras do grupo foram redefinidas com sucesso.',
                                    reply_to_message_id=msg['message_id'])
                else:
                    set_rules(msg['chat']['id'], msg['text'].split(' ', 1)[1])
                    bot.sendMessage(msg['chat']['id'], 'As regras do grupo foram definidas com sucesso.',
                                    reply_to_message_id=msg['message_id'])
