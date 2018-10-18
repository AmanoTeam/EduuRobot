import json
import config
import os

bot = config.bot
bot_username = config.bot_username


def jsondump(msg):
    if msg.get('text'):
        if msg['text'].startswith('/jsondump') or msg['text'].startswith('!jsondump') or msg['text'] == '/jsondump@' + bot_username:
            try:
                if '-f' not in msg['text']:
                    bot.sendMessage(msg['chat']['id'], '`' + json.dumps(msg, indent=2, sort_keys=False) + '`',
                                    'Markdown', reply_to_message_id=msg['message_id'])
                else:
                    bot.sendChatAction(msg['chat']['id'], 'upload_document')
                    with open('dump.json', 'wb') as i:
                        i.write(bytes(str(json.dumps(msg, indent=2, sort_keys=False)), 'utf-8'))
                    bot.sendDocument(msg['chat']['id'], open('dump.json', 'rb'), reply_to_message_id=msg['message_id']
                                     )
                    os.remove('dump.json')
            except:
                bot.sendChatAction(msg['chat']['id'], 'upload_document')
                with open('dump.json', 'wb') as i:
                    i.write(bytes(str(json.dumps(msg, indent=2, sort_keys=False)), 'utf-8'))
                bot.sendDocument(msg['chat']['id'], open('dump.json', 'rb'),
                                 reply_to_message_id=msg['message_id'])
                os.remove('dump.json')
            return True
