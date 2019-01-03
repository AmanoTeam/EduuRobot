import sqlite3
from sqlite3 import OperationalError

conn = sqlite3.connect('bot.db', check_same_thread=False)

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS chats (chat_id,
                                                    welcome,
                                                    welcome_enabled,
                                                    rules,
                                                    goodbye,
                                                    goodbye_enabled,
                                                    ia,
                                                    warns_limit,
                                                    antichato_enabled,
                                                    antichato_list)''')

cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id, ia)')

cursor.execute('CREATE TABLE IF NOT EXISTS channels (chat_id)')

cursor.execute('CREATE TABLE IF NOT EXISTS user_warns (user_id, chat_id, count)')

cursor.execute('CREATE TABLE IF NOT EXISTS was_restarted_on (chat_id, message_id)')


def chat_exists(chat_id):
    cursor.execute('SELECT * FROM chats WHERE chat_id = (?)', (chat_id,))
    if cursor.fetchall():
        return True
    else:
        return False


def channel_exists(chat_id):
    cursor.execute('SELECT * FROM channels WHERE chat_id = (?)', (chat_id,))
    if cursor.fetchall():
        return True
    else:
        return False


def user_exists(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = (?)', (user_id,))
    if cursor.fetchall():
        return True
    else:
        return False


def del_restarted():
    cursor.execute('DELETE FROM was_restarted_on')
    conn.commit()


def add_chat(chat_type, chat_id):
    if chat_type == 'private':
        if not user_exists(chat_id):
            cursor.execute('INSERT INTO users (user_id) VALUES (?)', (chat_id,))
            conn.commit()
    elif chat_type == 'supergroup' or chat_type == 'group':
        if not chat_exists(chat_id):
            cursor.execute('INSERT INTO chats (chat_id, welcome_enabled, antichato_list) VALUES (?,?,?)', (chat_id, True, '[]'))
            conn.commit()
    elif chat_type == 'channel':
         if not channel_exists(chat_id):
            cursor.execute('INSERT INTO channels (chat_id) VALUES (?)', (chat_id,))
            conn.commit()
    


def get_restarted():
    cursor.execute('SELECT * FROM was_restarted_on')
    try:
        return cursor.fetchall()[0]
    except IndexError:
        return None


def set_restarted(chat_id, message_id):
    cursor.execute('INSERT INTO was_restarted_on VALUES (?, ?)', (chat_id, message_id))
    conn.commit()
