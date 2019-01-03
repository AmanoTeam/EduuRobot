import config
import requests

bot = config.bot


def ip(msg):
    if msg.get('text'):
        if msg['text'].split()[0] == '/ip' or msg['text'].split()[0] == '!ip':
            text = msg['text'][4:].split('://')[-1]
            if text == '':
                bot.sendMessage(msg['chat']['id'], '*Uso:* `/ip IP/endereço`',
                                parse_mode='Markdown',
                                reply_to_message_id=msg['message_id'])
            else:
                req = requests.get('http://ip-api.com/json/' + text).json()
                x = ''
                for i in req:
                    x += "*{}*: `{}`\n".format(i.title(), req[i])
                bot.sendMessage(msg['chat']['id'], x, 'Markdown',
                                reply_to_message_id=msg['message_id'])
