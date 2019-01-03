from config import bot, keys
import requests


owm_key = keys['openweathermap']

get_coords = 'http://maps.google.com/maps/api/geocode/json'
url = 'http://api.openweathermap.org/data/2.5/weather/?q={}&units=metric&lang=pt&appid={}'

OFFSET = 127462 - ord('A')


def flag(code):
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)


def clima(msg):
    if msg.get('text'):
        if msg['text'].startswith('/clima'):
            if msg['text'][7:] == '':
                res = '*Uso:* `/clima <cidade>` - _Obtem informações meteorológicas da cidade._'
            else:
                json = requests.post(url.format(msg['text'][7:], owm_key)).json()
                if json['cod'] != 200:
                    print(json)
                    res = json['message']
                else:
                    res = '''Clima em *{}*, {}:

Clima: `{}`
Temperatura min.: `{} °C`
Temperatura máx.: `{} °C`
Umidade do ar: `{}%`
Vento: `{:.2f} m/s`'''.format(json['name'], flag(json['sys']['country']),
                              json['weather'][0]['description'], json['main']['temp_min'],
                              json['main']['temp_max'], json['main']['humidity'], json['wind']['speed'])
            bot.sendMessage(msg['chat']['id'], res, 'Markdown', reply_to_message_id=msg['message_id'])
            return True
