import config
from db_handler import conn, cursor

bot = config.bot


def get_welcome(chat_id):
    cursor.execute('SELECT (welcome, welcome_enabled) FROM chats WHERE chat_id = (?)', (chat_id,))
    try:
        return cursor.fetchall()[0]
    except IndexError:
        return None


def set_welcome(chat_id, welcome):
    try:
        cursor.execute('UPDATE chats SET welcome = ? welcome_set = True WHERE chat_id = ?', (welcome, chat_id))
    finally:
        cursor.execute('INSERT INTO chats (chat_id, welcome) VALUES (?, ?)', (chat_id, welcome))
    conn.commit()


def welcome(msg):
    pass