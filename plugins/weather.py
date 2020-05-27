# Copyright (C) 2018-2020 Amano Team <contact@amanoteam.com>
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

import re
import json
import aiohttp

from config import bot, keys

# That api key were publicly shown some time ago, and it still work.
weather_apikey = 'd522aa97197fd864d36b418f39ebb323'

get_coords = 'https://api.weather.com/v3/location/search'
url = 'https://weather.com/pt-BR/clima/hoje/l'

headers = {"Accept-Encoding", "gzip"}


async def weather(msg):
    if msg.get('text'):
        if msg['text'].startswith('/clima'):
            if msg['text'][7:] == '':
                res = '*Uso:* `/clima <cidade>` - _Obtem informações meteorológicas da cidade._'
            else:
                async with aiohttp.ClientSession() as session:
                    r = await session.get(get_coords, headers=headers,
                                                      params=dict(apiKey=weather_apikey,
                                                                  format="json",
                                                                  language="pt-BR",
                                                                  query=msg['text'][7:]))
                    loc_json = await r.json()
                if not gjson.get("location"):
                    return await bot.sendMessage(msg['chat']['id'], 'Localização não encontrada',
                                                 reply_to_message_id=msg['message_id'])
                else:
                    pos = loc_json['location']['placeId'][0]
                    async with aiohttp.ClientSession() as session:
                        r = await session.get(f"{url}/{pos}", headers=headers)
                        res_text = await r.text()
                    res_json = re.findall(r'__data=({.*?});', res_text)
                    # If the returned list is empty...
                    if not res_json:
                        return await bot.sendMessage(msg['chat']['id'], 'Esta localização não possui dados meteorológicos.',
                                                     reply_to_message_id=msg['message_id'])
                    res_json = json.loads(res_json[0])

                    loc_key = next(iter(res_json['dal']['Location']))
                    loc_dict = res_json['dal']['Location'][loc_key]['data']['location']

                    obs_key = next(iter(res_json['dal']['Observation']))
                    obs_dict = res_json['dal']['Observation'][obs_key]['data']['vt1observation']

                    res = '''*{}, {} - {}*:

Temperatura: `{} °C`
Sensação térmica: `{} °C`
Umidade do Ar: `{}%`
Vento: `{} km/h`

- _{}_'''.format(loc_dict['city'],
                 loc_dict['adminDistrict'],
                 loc_dict['country'],

                 obs_dict['temperature'],
                 obs_dict['feelsLike'],
                 obs_dict['humidity'],
                 obs_dict['windSpeed'],
                 obs_dict['phrase'])

            await bot.sendMessage(msg['chat']['id'], res, 'Markdown', reply_to_message_id=msg['message_id'])
            return True
