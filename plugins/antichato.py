import config
import json
from db_handler import conn, cursor


def get_antichato(chat_id):
    cursor.execute('SELECT (antichato_enabled, antichato_list) FROM chats WHERE chat_id = ?', (chat_id,))
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
        if ac[0] and msg['from']['id'] in ac[1]:
            bot.sendMessage(msg['chat']['id'], 'Test', reply_to_message_id=msg['message_id'])