import config
import requests
import random

bot = config.bot
bot_username = config.bot_username
giphy_key = config.keys['giphy']


def gif(msg):
    if msg.get('text'):
        if msg['text'].startswith('/gif ') or msg['text'].startswith('!gif '):
            text = msg['text'][5:]
            rjson = requests.get(
                "http://api.giphy.com/v1/gifs/search", params=dict(q=text, api_key=giphy_key, limit=7)).json()
            res = random.choice(rjson["data"])
            result = res["images"]["original_mp4"]["mp4"]
            bot.sendVideo(
                chat_id=msg['chat']['id'],
                video=result,
                reply_to_message_id=msg['message_id'])
