from config import bot
import requests
import time
import os


def prints(msg):
    if msg.get('text'):
        if msg['text'].startswith('/print ') or msg['text'].startswith('!print '):
            try:
                sent = bot.sendMessage(msg['chat']['id'], 'Tirando print...',
                                reply_to_message_id=msg['message_id'])
                ctime = time.time()
                if re.match(r'^https?:\/\/', msg['text'][7:]):
                    url = msg['text'][7:]
                else:
                    url = 'http://'+msg['text'][7:]
                requests.get("https://image.thum.io/get/width/1000/"+url)
                # We need to to a request again to prevent the bot from getting a GIF instead of a PNG file.
                r = requests.get("https://image.thum.io/get/width/1000/"+url)
                with open(f'{ctime}.png', 'wb') as f:
                    f.write(r.content)

                bot.sendPhoto(msg['chat']['id'],
                              open(f'{ctime}.png', 'rb'),
                              reply_to_message_id=msg['message_id'])
                bot.deleteMessage((msg['chat']['id'], sent['message_id']))
            except Exception as e:
                bot.editMessageText((msg['chat']['id'], sent['message_id']), f'Ocorreu um erro ao enviar a print, favor tente mais tarde.\nErro: {e}')
            finally:
                os.remove(f'{ctime}.png')
            return True
