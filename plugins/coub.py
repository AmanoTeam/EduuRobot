import config
import requests
import random

bot = config.bot
bot_username = config.bot_username


def coub(msg):
    if msg.get('text'):
        if msg['text'].startswith('/coub ') or msg['text'].startswith('!coub '):
            text = msg['text'][6:]
            try:
                r = requests.get(f'https://coub.com/api/v2/search/coubs?q={text}')
                content = random.choice(r.json()['coubs'])
                links = content['permalink']
                title = content['title']
                bot.sendMessage(msg['chat']['id'], f'*{title}*[\u00AD](https://coub.com/v/{links})',
                                reply_to_message_id=msg['message_id'], parse_mode="Markdown")
            except IndexError:
                bot.sendMessage(msg['chat']['id'], 'Not Found!', reply_to_message_id=msg['message_id'])
