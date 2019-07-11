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

import re
import json
import aiohttp

from config import bot, keys
from utils import get_flag

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
                    wjson = re.findall(r'__data=({.*?});', rtext)
                    # If the returned list is empty...
                    if not wjson:
                        return await bot.sendMessage(msg['chat']['id'], 'Esta localização não possui dados meteorológicos.',
                                                     reply_to_message_id=msg['message_id'])
                    wjson = json.loads(wjson[0])
                    fkey = list(wjson['dal']['Location'])[0]
                    fkey2 = list(wjson['dal']['Observation'])[0]
                    res = '''*{}, {} - {}*:

Temperatura: `{} °C`
Sensação térmica: `{} °C`
Umidade do Ar: `{}%`
Vento: `{} km/h`

- _{}_'''.format(wjson['dal']['Location'][fkey]['data']['location']['city'],
                 wjson['dal']['Location'][fkey]['data']['location']['adminDistrict'],
                 wjson['dal']['Location'][fkey]['data']['location']['country'],
                 wjson['dal']['Observation'][fkey2]['data']['vt1observation']['temperature'],
                 wjson['dal']['Observation'][fkey2]['data']['vt1observation']['feelsLike'],
                 wjson['dal']['Observation'][fkey2]['data']['vt1observation']['humidity'],
                 wjson['dal']['Observation'][fkey2]['data']['vt1observation']['windSpeed'],
                 wjson['dal']['Observation'][fkey2]['data']['vt1observation']['phrase'])
            await bot.sendMessage(msg['chat']['id'], res, 'Markdown', reply_to_message_id=msg['message_id'])
            return True
