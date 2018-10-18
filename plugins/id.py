import config

bot = config.bot


def id(msg):
    if msg.get('text'):
        if msg['text'] == '/id' or msg['text'] == '!id':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], '''
*Informações:*

*Nome:* `{}`
*Sobrenome:* `{}`
*Username:* `{}`
*ID:* `{}`
*Idioma:* `{}`
*Tipo de chat:* `{}`'''.format(
                    msg['from']['first_name'],
                    msg['from']['last_name'],
                    'username',
                    msg['from']['id'],
                    msg['from']['language_code'],
                    msg['chat']['type']
                ),
                                parse_mode='Markdown',
                                reply_to_message_id=msg['message_id']
                                )
            else:
                message_id = bot.sendMessage(
                    chat_id=msg['chat']['id'],
                    text='⏰ Consultando informações...',
                    reply_to_message_id=msg['message_id']
                )['message_id']
                chat_title = msg['chat']['title']
                members = bot.getChatMembersCount(msg['chat']['id'])
                if 'username' in msg['chat']:
                    chat_username = '@' + msg['chat']['username']
                else:
                    chat_username = 'nenhum'
                if 'language_code' in msg['from']:
                    lang_code = msg['from']['language_code']
                else:
                    lang_code = '-'
                first_name = msg['from']['first_name']
                if 'last_name' in msg['from']:
                    last_name = msg['from']['last_name']
                else:
                    last_name = ''
                if 'username' in msg['from']:
                    username = '@' + msg['from']['username']
                else:
                    username = 'nenhum'
                user_id = msg['from']['id']
                if 'reply_to_message' in msg:
                    from_info = msg['reply_to_message']['from']
                    first_name = from_info['first_name']

                    if 'last_name' in from_info:
                        last_name = from_info['last_name']
                    else:
                        last_name = ''

                    user_id = from_info['id']

                    if 'username' in from_info:
                        username = '@' + from_info['username']
                    else:
                        username = 'nenhum'

                    if 'language_code' in from_info:
                        lang_code = from_info['language_code']
                    else:
                        lang_code = '-'

                bot.editMessageText(
                    (msg['chat']['id'], message_id),
                    text='''
*Informações do chat:*

*Nome:* `{}`
*Sobrenome:* `{}`
*Username:* `{}`
*ID:* `{}`
*Idioma:* `{}`

*Nome do grupo:* `{}`
*Username do grupo:* `{}`
*ID do chat:* `{}`
*Total de mensagens:* `{}`
*Tipo de chat:* `{}`
*Total de membros:* `{}`'''.format(
                        first_name,
                        last_name,
                        username,
                        user_id,
                        lang_code,
                        msg['chat']['title'],
                        chat_username,
                        msg['chat']['id'],
                        msg['message_id'],
                        msg['chat']['type'],
                        members
                    ),
                    parse_mode='Markdown'
                )
            return True
