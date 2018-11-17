import config
from db_handler import conn, cursor

bot = config.bot
bot_username = config.bot_username


def escape(text):
    text = text.replace('[', '\[')
    text = text.replace('_', '\_')
    text = text.replace('*', '\*')
    text = text.replace('`', '\`')
    return text


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
    if msg.get('new_chat_member'):
        chat_title = msg['chat']['title']
        first_name = msg['new_chat_member']['first_name']
        user_id = msg['new_chat_member']['id']
        if msg['new_chat_member']['id'] == bot_id:
            bot.sendMessage(
                chat_id=200097591,
                text='''O bot foi adicionado em um novo grupo!

Nome do grupo: {}
ID do grupo: {}'''.format(msg['chat']['title'], msg['chat']['id']))
        else:
            welcome = get_welcome(chat_id)
            if welcome != None:
                welcome = welcome.replace('$name', md_utils.escape(first_name)).replace('$title', md_utils.escape(chat_title)).replace('$id', str(user_id))
            else:
                welcome = 'Olá {}, seja bem-vindo(a) ao {}!'.format(first_name,md_utils.escape(chat_title))
            if '$rules' in welcome:
                welcome = welcome.replace('$rules', '')
                rules_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Leia as regras',
                              url='https://t.me/{}?start=rules_{}'.format(bot_username, chat_id))]
                ])
            else:
                rules_markup = None
            bot.sendMessage(chat_id, welcome, 'Markdown',
                            reply_to_message_id=msg_id,
                            reply_markup=rules_markup,
                            disable_web_page_preview=True)