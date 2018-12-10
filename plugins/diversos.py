import config
import requests
import re
import html
import amanobot
from amanobot.exception import UnauthorizedError

bot = config.bot
sudos = config.sudoers
logs = config.logs
bot_username = config.bot_username


def send_to_hastebin(text):
    post = requests.post("https://hastebin.com/documents", data=text.encode('utf-8'))
    return "https://hastebin.com/" + post.json()["key"]


def diversos(msg):
    if msg.get('text'):

        if msg['text'].startswith('/echo ') or msg['text'].startswith('!echo '):
            if msg.get('reply_to_message'):
                reply_id = msg['reply_to_message']['message_id']
            else:
                reply_id = None
            bot.sendMessage(msg['chat']['id'], msg['text'][6:],
                            reply_to_message_id=reply_id)
            return True


        elif msg['text'].startswith('/mark ') or msg['text'].startswith('!mark '):
            if msg.get('reply_to_message'):
                reply_id = msg['reply_to_message']['message_id']
            else:
                reply_id = None
            bot.sendMessage(msg['chat']['id'], msg['text'][6:], 'markdown',
                            reply_to_message_id=reply_id)
            return True


        elif msg['text'] == '/admins' or msg['text'] == '!admins':
            adms = bot.getChatAdministrators(msg['chat']['id'])
            names = 'Admins:\n\n'
            for num, user in enumerate(adms):
                names += '{} - <a href="tg://user?id={}">{}</a>\n'.format(num+1, user['user']['id'],
                    html.escape(user['user']['first_name']))
            bot.sendMessage(msg['chat']['id'], names, 'html',
                            reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/token ') or msg['text'].startswith('!token '):
            text = msg['text'][7:]
            try:
                bot = amanobot.Bot(text).getMe()
                bot_name = bot_token['first_name']
                bot_user = bot_token['username']
                bot_id = bot_token['id']
                bot.sendMessage(msg['chat']['id'], '''Informações do bot:

Nome: {}
Username: @{}
ID: {}'''.format(bot_name, bot_user, bot_id), reply_to_message_id=msg['message_id'])

            except UnauthorizedError:
                bot.sendMessage(msg['chat']['id'], 'Token inválido.',
                                reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/bug') or msg['text'].startswith('!bug'):
            text = msg['text'][5:]
            if text == '' or text == bot_username:
                bot.sendMessage(msg['chat']['id'], '''*Uso:* `/bug <descrição do bug>` - _Reporta erro/bug para minha equipe_
  obs.: Mal uso há possibilidade de ID\_ban''', 'markdown',
                                reply_to_message_id=msg['message_id'])
            else:
                bot.sendMessage(logs, '''
<a href="tg://user?id={}">{}</a> reportou um bug

ID: <code>{}</code>
Mensagem: {}'''.format(msg['from']['id'],
                       msg['from']['first_name'],
                       msg['from']['id'],
                       text), 'HTML')
                bot.sendMessage(msg['chat']['id'], 'O bug foi reportado com sucesso para a minha equipe!',
                                reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/html ') or msg['text'].startswith('!html '):
            if msg.get('reply_to_message'):
                reply_id = msg['reply_to_message']['message_id']
            else:
                reply_id = None
            bot.sendMessage(msg['chat']['id'], msg['text'][6:], 'html',
                            reply_to_message_id=reply_id)
            return True


        elif msg['text'].startswith('/text ') or msg['text'].startswith('!text '):
            string = ''
            text = msg['text'][6:]
            if msg.get('reply_to_message'):
                reply_id = msg['reply_to_message']['message_id']
            else:
                reply_id = None
            sent = bot.sendMessage(msg['chat']['id'], '<code>|</code>', 'html',
                                   reply_to_message_id=reply_id)
            for char in text:
                string = string + char
                bot.editMessageText((msg['chat']['id'], sent['message_id']), '<code>' + string + '</code>', 'html')
                bot.editMessageText((msg['chat']['id'], sent['message_id']), '<code>' + string + '|</code>', 'html')
            bot.editMessageText((msg['chat']['id'], sent['message_id']), '<code>' + msg['text'][6:] + '</code>', 'html')
            return True


        elif msg['text'].startswith('/request ') or msg['text'].startswith('!request '):
            if re.match(r'^(https?:\/\/)', msg['text'][9:]):
                text = msg['text'][9:]
            else:
                text = 'http://' + msg['text'][9:]
            try:
                res = requests.get(text).text
            except Exception as e:
                return bot.sendMessage(msg['chat']['id'], str(e),
                                       reply_to_message_id=msg['message_id'])
            if len(res) > 4000:
                res = send_to_hastebin(res)
            bot.sendMessage(msg['chat']['id'], '*Conteúdo:*\n`{}`'.format(res), 'markdown',
                            reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/suco'):
            if msg['from']['id'] in sudos:
                l = '✅'
            else:
                l = '❌'
            bot.sendMessage(msg['chat']['id'], l + '🍹',
                            reply_to_message_id=msg['message_id'])


        elif msg['text'].lower() == 'rt' and msg.get('reply_to_message'):
            if msg['reply_to_message']['text'].lower() != 'rt':
                if not re.match('🔃 .* retweetou:\n\n👤 .*', msg['reply_to_message']['text']):
                    bot.sendMessage(msg['chat']['id'], '''🔃 <b>{}</b> retweetou:

👤 <b>{}</b>: <i>{}</i>'''.format(msg['from']['first_name'], msg['reply_to_message']['from']['first_name'],
                                  msg['reply_to_message']['text']), 'HTML',
                                    reply_to_message_id=msg['message_id'])
                    return True
