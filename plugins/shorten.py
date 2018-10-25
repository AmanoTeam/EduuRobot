import config
import requests

bot = config.bot

def shorten(msg):
    if msg.get('text'):
        if msg['text'].startswith('/shorten'):
            text = msg['text'][9:]
            if text == '':
                bot.sendMessage(msg['chat']['id'], '*Uso:* `/shorten google.com` - _Encurta uma URL. Powered by_ 🇧🇷.ml', 'Markdown', reply_to_message_id=msg['message_id'])
            else:
                r = requests.post('https://amanosite.000webhostapp.com/api/', data=dict(url=text))
                bot.sendMessage(msg['chat']['id'], '*Resultado:* {}'.format(r.json()['result']), 'Markdown',
                                reply_to_message_id=msg['message_id'])