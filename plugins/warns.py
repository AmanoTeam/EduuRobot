import config
from .admins import isAdmin
from db_handler import cursor, conn

bot = config.bot


def get_warns(chat_id, user_id):
    cursor.execute('SELECT count FROM user_warns WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    return cursor.fetchall()[0][0]


def get_warns_limit(chat_id):
    cursor.execute('SELECT warns_limit FROM chats WHERE chat_id = ?', (chat_id,))
    return cursor.fetchall()[0][0]


def add_warns(chat_id, user_id, number):
    cursor.execute('SELECT * FROM user_warns WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    if cursor.fetchall():
        cursor.execute('UPDATE user_warns SET count = count + ? WHERE chat_id = ? AND user_id = ?', (number, chat_id, user_id))
        conn.commit()
    else:
        cursor.execute('INSERT INTO user_warns (user_id, chat_id, count) VALUES (?,?,?)', (user_id, chat_id, number))
        conn.commit()
    return True


def warns(msg):
    if msg.get('text'):
        if msg['text'].split()[0] == '/warn' or msg['text'].split()[0] == '!warn':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            else:
                warns_limit = get_warns_limit(msg['chat']['id']) or 3
                if msg.get('reply_to_message'):
                    reply_id = msg['reply_to_message']['from']['id']
                    reply_name = msg['reply_to_message']['from']['first_name']
                elif len(msg['text'].split()) > 1:
                    u_id = msg['text'].split()[1]
                    try:
                        get = bot.getChat(u_id)
                        reply_id = get['id']
                        reply_name = get['first_name']
                    except:
                        bot.sendMessage(msg['chat']['id'], 'ID inválida ou desconhecida. use nesse formato: /warn ID do usuário',
                                        reply_to_message_id=msg['message_id'])
                        return
                else:
                    reply_id = None

                adm = isAdmin(msg['chat']['id'], msg['from']['id'], reply_id)

                if adm['user']:
                    try:
                        int(reply_id)
                    except:
                        return bot.sendMessage(msg['chat']['id'], 'Responda alguém ou informe sua ID',
                                               reply_to_message_id=msg['message_id'])
                    if adm['bot']:
                        if adm['reply']:
                            bot.sendMessage(msg['chat']['id'], 'Esse aí tem admin',
                                            reply_to_message_id=msg['message_id'])
                        else:
                            add_warns(msg['chat']['id'], reply_id, 1)
                            user_warns = get_warns(msg['chat']['id'], reply_id)
                            if user_warns >= warns_limit:
                                bot.kickChatMember(msg['chat']['id'], reply_id)
                                bot.sendMessage(msg['chat']['id'], '{} banido pois atingiu o limite de advertências'.format(reply_name),
                                                reply_to_message_id=msg['message_id'])
                            else:
                                bot.sendMessage(msg['chat']['id'], '{} Foi advertido ({}/{})'.format(reply_name, user_warns, warns_limit),
                                                reply_to_message_id=msg['message_id'])
                    else:
                        bot.sendMessage(msg['chat']['id'], 'Ei, eu nao tenho admin aqui',
                                        reply_to_message_id=msg['message_id'])
            return True