# Copyright (C) 2018-2019 Amano Team <contact@amanoteam.ml>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from config import bot, bot_username


async def ids(msg):
    if msg.get('text'):
        if msg['text'] == '/id' or msg['text'] == '!id' or msg['text'] == '/id@' + bot_username:
            if msg['chat']['type'] == 'private':
                if 'last_name' in msg['from']:
                    last_name = msg['from']['last_name']
                else:
                    last_name = ''
                if 'username' in msg['from']:
                    username = '@' + msg['from']['username']
                else:
                    username = ''
                await bot.sendMessage(msg['chat']['id'], '''
*Informações:*

*Nome:* `{}`{}{}
*ID:* `{}`
*Idioma:* `{}`
*Tipo de chat:* `{}`'''.format(msg['from']['first_name'],
                               '\n*Sobrenome:* `{}`'.format(last_name) if last_name != '' else '',
                               '\n*Último nome:* `{}`'.format(username) if username != '' else '',
                               msg['from']['id'],
                               msg['from']['language_code'],
                               msg['chat']['type']),
                                      parse_mode='Markdown',
                                      reply_to_message_id=msg['message_id'])
            else:
                sent = await bot.sendMessage(msg['chat']['id'], '⏰ Consultando informações...',
                                             reply_to_message_id=msg['message_id'])
                members = await bot.getChatMembersCount(msg['chat']['id'])
                if 'username' in msg['chat']:
                    chat_username = '@' + msg['chat']['username']
                else:
                    chat_username = ''
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
                    username = ''
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
                        username = ''

                    if 'language_code' in from_info:
                        lang_code = from_info['language_code']
                    else:
                        lang_code = '-'

                await bot.editMessageText(
                    (msg['chat']['id'], sent['message_id']),
                    text='''
*Informações do chat:*

*Nome:* `{}`{}{}
*ID:* `{}`
*Idioma:* `{}`

*Nome do grupo:* `{}`{}
*ID do grupo:* `{}`
*Mensagens:* `{}`
*Tipo de chat:* `{}`
*Membros:* `{}`'''.format(
                        first_name,
                        '\n*Último nome:* `{}`'.format(last_name) if last_name != '' else '',
                        '\n*Username:* `{}`'.format(username) if username != '' else '',
                        user_id,
                        lang_code,
                        msg['chat']['title'],
                        '\n*Username do grupo:* `{}`'.format(chat_username) if chat_username != '' else '',
                        msg['chat']['id'],
                        msg['message_id'],
                        msg['chat']['type'],
                        members
                    ),
                    parse_mode='Markdown'
                )
            return True
