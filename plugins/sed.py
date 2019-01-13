from config import bot
import re
import html
import signal


def timeout_exception(*args):
    bot.sendMessage(msg['chat']['id'], 'Um padrão regex não pode executar por mais de 1 segundo.')
    return True


def sed(msg):
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

            signal.signal(signal.SIGALRM, timeout_exception)
            globals()['msg'] = msg

            signal.alarm(1)
            res = re.sub(pattern, replace_with, text, count=count, flags=rflags)
            signal.alarm(0)

            bot.sendMessage(msg['chat']['id'], f'<pre>{html.escape(res)}</pre>', 'html',
                            reply_to_message_id=msg['reply_to_message']['message_id'])

            return True
