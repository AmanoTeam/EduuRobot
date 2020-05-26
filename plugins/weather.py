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

here_keys = keys['here']

get_coords = 'https://geocoder.api.here.com/6.2/geocode.json'
url = 'https://weather.com/pt-BR/clima/hoje/l'


async def weather(msg):
    if msg.get('text'):
        if msg['text'].startswith('/clima'):
            if msg['text'][7:] == '':
                res = '*Uso:* `/clima <cidade>` - _Obtem informações meteorológicas da cidade._'
            else:
                async with aiohttp.ClientSession() as session:
                    r = await session.get(get_coords, params=dict(searchtext=msg['text'][7:],
                                                                  app_id=here_keys['app_id'],
                                                                  app_code=here_keys['app_code']))
                    gjson = await r.json()
                if len(gjson['Response']['View']) == 0:
                    return await bot.sendMessage(msg['chat']['id'], 'Localização não encontrada',
                                                 reply_to_message_id=msg['message_id'])
                else:
                    pos = gjson['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']
                    async with aiohttp.ClientSession() as session:
                        r = await session.get(f"{url}/{pos['Latitude']},{pos['Longitude']}")
                        rtext = await r.text()
                    wjson = re.findall(r'__data=({.*?});<', rtext)
                    # If the returned list is empty...
                    if not wjson:
                        return await bot.sendMessage(msg['chat']['id'], 'Esta localização não possui dados meteorológicos.',
                                                     reply_to_message_id=msg['message_id'])
                    wjson = json.loads(wjson[0])
                    fkey = list(wjson['dal']['getSunV3LocationPointUrlConfig'])[0]
                    fkey2 = list(wjson['dal']['getSunV3CurrentObservationsUrlConfig'])[0]
                    res = '''*{}, {} - {}*:

Temperatura: `{} °C`
Sensação térmica: `{} °C`
Umidade do Ar: `{}%`
Vento: `{} km/h`

- _{}_'''.format(wjson['dal']['getSunV3LocationPointUrlConfig'][fkey]['data']['location']['city'],
                 wjson['dal']['getSunV3LocationPointUrlConfig'][fkey]['data']['location']['adminDistrict'],
                 wjson['dal']['getSunV3LocationPointUrlConfig'][fkey]['data']['location']['country'],
                 wjson['dal']['getSunV3CurrentObservationsUrlConfig'][fkey2]['data']['temperature'],
                 wjson['dal']['getSunV3CurrentObservationsUrlConfig'][fkey2]['data']['temperatureFeelsLike'],
                 wjson['dal']['getSunV3CurrentObservationsUrlConfig'][fkey2]['data']['relativeHumidity'],
                 wjson['dal']['getSunV3CurrentObservationsUrlConfig'][fkey2]['data']['windSpeed'],
                 wjson['dal']['getSunV3CurrentObservationsUrlConfig'][fkey2]['data']['cloudCoverPhrase'])
            await bot.sendMessage(msg['chat']['id'], res, 'Markdown', reply_to_message_id=msg['message_id'])
            return True
