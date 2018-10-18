import config
import os

bot = config.bot


def prints(msg):
    if msg.get('text'):
        if msg['text'].startswith('/print ') or msg['text'].startswith('!print '):
            driver.get(msg['text'][7:])
            driver.save_screenshot('{}.png'.format(msg['from']['id']))
            bot.sendPhoto(msg['chat']['id'], open('{}.png'.format(msg['from']['id']), 'rb'),
                          reply_to_message_id=msg['message_id']
                          )
            os.remove('{}.png'.format(msg['from']['id']))
            return True
