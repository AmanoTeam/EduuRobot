import config
import re
import html

bot = config.bot


def sed(msg):
    if msg.get('text'):
        if msg['text'].startswith('s/') and msg.get('reply_to_message'):
            exp = re.split(r'(?<![^\\]\\)/', msg['text'])
            pattern = exp[1]
            replace_with = exp[2]
            flags = exp[3] if len(exp) > 3 else 'g'

            res = re.sub(pattern, replace_with, msg['reply_to_message']['text'], flags=flags)

            bot.sendMessage(msg['chat']['id'], f'<pre>{html.escape(res)}</pre>', 'html',
                            reply_to_message_id=msg['reply_to_message']['message_id'])

            return True

