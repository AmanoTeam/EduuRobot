from config import bot, bot_username, bot_id
from amanobot.namedtuple import InlineKeyboardMarkup
from db_handler import conn, cursor
from .admins import is_admin


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
    cursor.execute('UPDATE chats SET welcome = ? WHERE chat_id = ?', (welcome, chat_id))
    conn.commit()


def enable_welcome(chat_id):
    cursor.execute('UPDATE chats SET welcome_enabled = ? WHERE chat_id = ?', (True, chat_id))
    conn.commit()


def disable_welcome(chat_id):
    cursor.execute('UPDATE chats SET welcome_enabled = ? WHERE chat_id = ?', (False, chat_id))
    conn.commit()


def welcome(msg):
    if msg.get('text'):
        if msg['text'].split()[0] == '/welcome' or msg['text'].split()[0] == '/welcome@'+bot_username or msg['text'].split()[0] == '!welcome':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')

            elif is_admin(msg['chat']['id'], msg['from']['id']):
                text = msg['text'].split(' ', 1)
                if len(text) == 1:
                    bot.sendMessage(msg['chat']['id'], 'Uso: /welcome on/off/reset/mensagem de boas-vindas do grupo (suporta Markdown e as tags $name, $title, $id e $rules)',
                                    reply_to_message_id=msg['message_id'])
                elif text[1] == 'on':
                    enable_welcome(msg['chat']['id'])
                    bot.sendMessage(msg['chat']['id'], 'A mensagem de boas-vindas foi ativada.',
                                    reply_to_message_id=msg['message_id'])
                elif text[1] == 'off':
                    disable_welcome(msg['chat']['id'])
                    bot.sendMessage(msg['chat']['id'], 'A mensagem de boas-vindas foi desativada.',
                                    reply_to_message_id=msg['message_id'])
                elif text[1] == 'reset':
                    set_welcome(msg['chat']['id'], None)
                    bot.sendMessage(msg['chat']['id'], 'A mensagem de boas-vindas foi redefinida.',
                                    reply_to_message_id=msg['message_id'])
                else:
                    set_welcome(msg['chat']['id'], text[1])
                    bot.sendMessage(msg['chat']['id'], 'A mensagem de boas-vindas foi definida.',
                                    reply_to_message_id=msg['message_id'])


    elif msg.get('new_chat_member'):
        chat_title = msg['chat']['title']
        chat_id = msg['chat']['id']
        first_name = msg['new_chat_member']['first_name']
        user_id = msg['new_chat_member']['id']
        if msg['new_chat_member']['id'] == bot_id:
            pass
        else:
            welcome = get_welcome(chat_id)
            if welcome[1]:
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
                