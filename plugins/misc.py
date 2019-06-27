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

import html
import re

import amanobot
import aiohttp
from amanobot.exception import TelegramError

from config import bot, sudoers, logs, bot_username
from utils import send_to_dogbin, send_to_hastebin


async def misc(msg):
    if msg.get('text'):

        if msg['text'].startswith('/echo ') or msg['text'].startswith('!echo '):
            if msg.get('reply_to_message'):
                reply_id = msg['reply_to_message']['message_id']
            else:
                reply_id = None
            await bot.sendMessage(msg['chat']['id'], msg['text'][6:],
                                  reply_to_message_id=reply_id)
            return True


        elif msg['text'].startswith('/mark ') or msg['text'].startswith('!mark '):
            if msg.get('reply_to_message'):
                reply_id = msg['reply_to_message']['message_id']
            else:
                reply_id = None
            await bot.sendMessage(msg['chat']['id'], msg['text'][6:], 'markdown',
                                  reply_to_message_id=reply_id)
            return True


        elif msg['text'] == '/admins' or msg['text'] == '!admins':
            if msg['chat']['type'] == 'private':
                await bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            else:
                adms = await bot.getChatAdministrators(msg['chat']['id'])
                names = 'Admins:\n\n'
                for num, user in enumerate(adms):
                    names += '{} - <a href="tg://user?id={}">{}</a>\n'.format(num + 1, user['user']['id'],
                                                                              html.escape(user['user']['first_name']))
                await bot.sendMessage(msg['chat']['id'], names, 'html',
                                      reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/token ') or msg['text'].startswith('!token '):
            text = msg['text'][7:]
            try:
                bot_token = amanobot.Bot(text).getMe()
                bot_name = bot_token['first_name']
                bot_user = bot_token['username']
                bot_id = bot_token['id']
                await bot.sendMessage(msg['chat']['id'], f'''Informações do bot:

Nome: {bot_name}
Username: @{bot_user}
ID: {bot_id}''',
                                      reply_to_message_id=msg['message_id'])

            except TelegramError:
                await bot.sendMessage(msg['chat']['id'], 'Token inválido.',
                                      reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/bug') or msg['text'].startswith('!bug'):
            text = msg['text'][5:]
            if text == '' or text == bot_username:
                await bot.sendMessage(msg['chat']['id'], '''*Uso:* `/bug <descrição do bug>` - _Reporta erro/bug para minha equipe_
  obs.: Mal uso há possibilidade de ID\_ban''', 'markdown',
                                      reply_to_message_id=msg['message_id'])
            else:
                await bot.sendMessage(logs, f"""<a href="tg://user?id={msg['from']['id']}">{msg['from'][
                    'first_name']}</a> reportou um bug:

ID: <code>{msg['from']['id']}</code>
Mensagem: {text}""", 'HTML')
                await bot.sendMessage(msg['chat']['id'], 'O bug foi reportado com sucesso para a minha equipe!',
                                      reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/dogbin') or msg['text'].startswith('!dogbin'):
            text = msg['text'][8:] or msg.get('reply_to_message', {}).get('text')
            if not text:
                await bot.sendMessage(msg['chat']['id'],
                                      '''*Uso:* `/dogbin <texto>` - _envia um texto para o del.dog._''',
                                      'markdown',
                                      reply_to_message_id=msg['message_id'])
            else:
                link = await send_to_dogbin(text)
                await bot.sendMessage(msg['chat']['id'], link, disable_web_page_preview=True,
                                      reply_to_message_id=msg['message_id'])
            return True

        elif msg['text'].startswith('/hastebin') or msg['text'].startswith('!hastebin'):
                text = msg['text'][9:] or msg.get('reply_to_message', {}).get('text')
                if not text:
                    await bot.sendMessage(msg['chat']['id'],
                                          '''*Uso:* `/hastebin <texto>` - _envia um texto para o hastebin._''',
                                          'markdown',
                                          reply_to_message_id=msg['message_id'])
                else:
                    link = await send_to_hastebin(text)
                    await bot.sendMessage(msg['chat']['id'], link, disable_web_page_preview=True,
                                          reply_to_message_id=msg['message_id'])
                return True

        elif msg['text'].startswith('/html ') or msg['text'].startswith('!html '):
            if msg.get('reply_to_message'):
                reply_id = msg['reply_to_message']['message_id']
            else:
                reply_id = None
            await bot.sendMessage(msg['chat']['id'], msg['text'][6:], 'html',
                                  reply_to_message_id=reply_id)
            return True


        elif msg['text'] == '/kickme' or msg['text'] == '!kickme':
            try:
                await bot.unbanChatMember(msg['chat']['id'], msg['from']['id'])
            except TelegramError:
                await bot.sendMessage(msg['chat']['id'],
                                      'Nao deu pra te remover, você deve ser um admin ou eu nao sou admin.',
                                      reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/request ') or msg['text'].startswith('!request '):
            if re.match(r'^(https?)://', msg['text'][9:]):
                text = msg['text'][9:]
            else:
                text = 'http://' + msg['text'][9:]
            try:
                async with aiohttp.ClientSession() as session:
                    r = await session.get(text)
            except Exception as e:
                return await bot.sendMessage(msg['chat']['id'], str(e),
                                             reply_to_message_id=msg['message_id'])
            headers = '<b>Status-Code:</b> <code>{}</code>\n'.format(str(r.status))
            headers += '\n'.join('<b>{}:</b> <code>{}</code>'.format(x, html.escape(r.headers[x])) for x in r.headers)
            rtext = await r.text()
            if len(rtext) > 3000:
                content = await r.read()
                res = await send_to_dogbin(content)
            else:
                res = '<code>' + html.escape(rtext) + '</code>'
            await bot.sendMessage(msg['chat']['id'], '<b>Headers:</b>\n{}\n\n<b>Conteúdo:</b>\n{}'.format(headers, res),
                                  'html', reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'] == '/suco':
            if msg['from']['id'] in sudoers:
                is_sudo = '✅'
            else:
                is_sudo = '❌'
            await bot.sendMessage(msg['chat']['id'], is_sudo + '🍹',
                                  reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].lower() == 'rt' and msg.get('reply_to_message'):
            if msg['reply_to_message'].get('text'):
                text = msg['reply_to_message']['text']
            elif msg['reply_to_message'].get('caption'):
                text = msg['reply_to_message']['caption']
            else:
                text = None
            if text:
                if text.lower() != 'rt':
                    if not re.match('🔃 .* retweetou:\n\n👤 .*', text):
                        await bot.sendMessage(msg['chat']['id'], '''🔃 <b>{}</b> retweetou:

👤 <b>{}</b>: <i>{}</i>'''.format(msg['from']['first_name'], msg['reply_to_message']['from']['first_name'],
                                  text),
                                              parse_mode='HTML',
                                              reply_to_message_id=msg['message_id'])
                return True
