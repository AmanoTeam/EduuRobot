import json
import config
import os
import html

bot = config.bot
bot_username = config.bot_username


def jsondump(msg):
    if msg.get('text'):
        if msg['text'].startswith('/jsondump') or msg['text'].startswith('!jsondump') or msg[
            'text'] == '/jsondump@' + bot_username:
            msgjson = json.dumps(msg, indent=2, sort_keys=False)
            if '-f' not in msg['text'] and len(msgjson) < 4080:
                    bot.sendMessage(msg['chat']['id'], '<pre>' + html.escape(msgjson) + '</pre>',
                                    'html', reply_to_message_id=msg['message_id'])
            else:
                bot.sendChatAction(msg['chat']['id'], 'upload_document')
                with open('dump.json', 'wb') as i:
                    i.write(msgjson.encode())
                bot.sendDocument(msg['chat']['id'], open('dump.json', 'rb'), reply_to_message_id=msg['message_id'])
                os.remove('dump.json')
            return True
