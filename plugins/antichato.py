import config
from db_handler import conn, cursor


def get_antipedro_enabled(chat_id):
	cursor.execute('SELECT antipedro_enabled FROM chats WHERE chat_id = ?', (chat_id,))


def antichato(msg):
	pass