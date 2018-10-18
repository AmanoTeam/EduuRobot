import sqlite3

conn = sqlite3.connect('bot.db', check_same_thread=False)

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                                                    chat_id,
                                                    type,
                                                    welcome,
                                                    welcome_set,
                                                    goodbye,
                                                    goodbye_set,
                                                    ia
                                                    )''')


cursor.execute('CREATE TABLE IF NOT EXISTS was_restarted_on (chat_id, message_id)')


def chat_exists(chat_id):
    try:
        cursor.execute('SELECT * FROM chats WHERE chat_id = (?)', (chat_id,))
        cursor.fetchall()[0]
        return True
    except IndexError:
        return False


def del_restarted():
    cursor.execute('DELETE FROM was_restarted_on')
    conn.commit()


def add_chat(chat_type, chat_id):
    if not chat_exists(chat_id):
        cursor.execute('INSERT INTO chats (chat_id, type) VALUES (?,?)', (chat_id, chat_type))
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


def get_welcome(chat_id):
    cursor.execute('SELECT (welcome, welcome_set) FROM chats WHERE chat_id = (?)', (chat_id,))
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
