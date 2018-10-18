import config
import random

bot = config.bot
bot_username = config.bot_username


def dados(msg):
    if msg.get('text'):
        if msg['text'] == '/dados' or msg['text'] == '!dados' or msg['text'] == '/dados@' + bot_username:
            dados = random.randint(1, 6)
            bot.sendMessage(msg['chat']['id'], '🎲 O dado parou no número: {}'.format(dados),
                            reply_to_message_id=msg['message_id']
                            )
            return True
