import config
import requests

bot = config.bot


def ip(msg):
    if msg.get('text'):
        if msg['text'].startswith('/ip') or msg['text'].startswith('!ip'):
            text = msg['text'][4:]
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
                try:
                    bot.sendLocation(msg['chat']['id'],
                                     latitude=req['lat'],
                                     longitude=req['lon'],
                                     reply_to_message_id=msg['message_id'])
                except KeyError:
                    pass
