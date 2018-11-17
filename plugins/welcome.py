import config
from db_handler import conn, cursor
from .admins import isAdmin

bot = config.bot
bot_username = config.bot_username
bot_id = config.bot_id


def escape(text):
    text = text.replace('[', '\[')
    text = text.replace('_', '\_')
    text = text.replace('*', '\*')
    text = text.replace('`', '\`')
    return text


def get_welcome(chat_id):
    cursor.execute('SELECT welcome, welcome_enabled FROM chats WHERE chat_id = (?)', (chat_id,))
    try:
        return cursor.fetchall()[0]
    except IndexError:
        return None


def set_welcome(chat_id, welcome):
    cursor.execute('UPDATE chats SET welcome = ?, welcome_enabled = True WHERE chat_id = ?', (welcome, chat_id))
    conn.commit()


def welcome(msg):
    if msg.get('text'):
        pass
    elif msg.get('new_chat_member'):
        chat_title = msg['chat']['title']
        chat_id = msg['chat']['id']
        first_name = msg['new_chat_member']['first_name']
        user_id = msg['new_chat_member']['id']
        if msg['new_chat_member']['id'] == bot_id:
            pass
        else:
            welcome = get_welcome(chat_id)
            if welcome[0] != None:
                welcome = welcome[0].replace('$name', escape(first_name)).replace('$title', escape(chat_title)).replace('$id', str(user_id))
            else:
                welcome = 'Olá {}, seja bem-vindo(a) ao {}!'.format(first_name, escape(chat_title))
            if '$rules' in welcome:
                welcome = welcome.replace('$rules', '')
                rules_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Leia as regras',
                              url='https://t.me/{}?start=rules_{}'.format(bot_username, chat_id))]
                ])
            else:
                rules_markup = None
            bot.sendMessage(chat_id, welcome, 'Markdown',
                            reply_to_message_id=msg['message_id'],
                            reply_markup=rules_markup,
                            disable_web_page_preview=True)