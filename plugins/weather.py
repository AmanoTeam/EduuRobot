# Copyright (C) 2018-2019 Amano Team <contact@amanoteam.ml>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import aiohttp

from config import bot, keys
from utils import get_flag

owm_key = keys['openweathermap']

get_coords = 'http://maps.google.com/maps/api/geocode/json'
url = 'http://api.openweathermap.org/data/2.5/weather/'


async def weather(msg):
    if msg.get('text'):
        if msg['text'].startswith('/clima'):
            if msg['text'][7:] == '':
                res = '*Uso:* `/clima <cidade>` - _Obtem informações meteorológicas da cidade._'
            else:
                async with aiohttp.ClientSession() as session:
                    r = await session.post(url, params=dict(q=msg['text'][7:],
                                                            units='mestrics',
                                                            lang='pt',
                                                            appid=owm_key
                    ))
                    json = await r.json()
                if json['cod'] != 200:
                    print(json)
                    res = json['message']
                else:
                    res = '''Clima em *{}*, {}:

Clima: `{}`
Temperatura min.: `{} °C`
Temperatura máx.: `{} °C`
Umidade do ar: `{}%`
Vento: `{:.2f} m/s`'''.format(json['name'], get_flag(json['sys']['country']),
                              json['weather'][0]['description'], json['main']['temp_min'],
                              json['main']['temp_max'], json['main']['humidity'], json['wind']['speed'])
            await bot.sendMessage(msg['chat']['id'], res, 'Markdown', reply_to_message_id=msg['message_id'])
            return True
