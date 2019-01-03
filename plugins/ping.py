from config import bot, bot_username
import time


def ping(msg):
    if msg.get('text'):
        if msg['text'] == '/ping' or msg['text'] == '!ping' or msg['text'] == '/ping@' + bot_username:
            first = time.time()
            sent = bot.sendMessage(msg['chat']['id'], '*Pong!*', 'Markdown', reply_to_message_id=msg['message_id'])[
                'message_id']
            second = time.time()
            bot.editMessageText((msg['chat']['id'], sent), '*Pong!* `{}`s'.format(str(second - first)[:5]), 'Markdown')
            return True

        elif msg['text'] == '/king' or msg['text'] == '!king' or msg['text'] == '/king@' + bot_username:
            bot.sendMessage(msg['chat']['id'], '*Kong!*', 'Markdown', reply_to_message_id=msg['message_id'])
            return True
