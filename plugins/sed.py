from config import bot
import re
import html
from threading import Thread, Event


stop = Event()


def timeout_exception(*args):
    
    return True


def replace():
    globals()['res'] = re.sub(pattern, replace_with, text, count=count, flags=rflags)


def sed(msg):
    global msg, pattern, replace_with, text, count, rflags
    if msg.get('text'):
        if re.match(r's/(.+)?/(.+)?(/.+)?', msg['text']) and msg.get('reply_to_message'):
            exp = re.split(r'(?<![^\\]\\)/', msg['text'])
            pattern = exp[1]
            replace_with = exp[2]
            flags = exp[3] if len(exp) > 3 else ''

            count = 1
            rflags = 0

            if 'i' in flags and 'g' in flags:
                count = 0
                rflags = re.I
            elif 'i' in flags:
                rflags = re.I
            elif 'g' in flags:
                count = 0

            if msg['reply_to_message'].get('text'):
                text = msg['reply_to_message']['text']
            if msg['reply_to_message'].get('caption'):
                text = msg['reply_to_message']['caption']

            t = Thread(target=replace)
            t.start()
            t.join(0.5)
            stop.set()

            if globals().get('res') is None:
                bot.sendMessage(msg['chat']['id'], 'Ocorreu um problema com o seu padrão regex.',
                                reply_to_message_id=msg['reply_to_message']['message_id'])
            else:
                bot.sendMessage(msg['chat']['id'], f'<pre>{html.escape(res)}</pre>', 'html',
                                reply_to_message_id=msg['reply_to_message']['message_id'])

            return True
