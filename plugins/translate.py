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

import html

import aiohttp

from config import bot, keys

traducao = keys['yandex']

idiomas = [
    'az', 'ml', 'sq', 'mt', 'am', 'mk', 'en', 'mi', 'ar', 'mr', 'hy', 'mhr', 'af', 'mn', 'eu', 'de', 'ba', 'ne', 'be',
    'no', 'bn', 'pa', 'my', 'pap', 'bg', 'fa', 'bs', 'pl', 'cy', 'pt', 'hu', 'ro', 'vi', 'ru', 'ht', 'ceb', 'gl', 'sr',
    'nl', 'si', 'mrj', 'sk', 'el', 'sl', 'ka', 'sw', 'gu', 'su', 'da', 'tg', 'he', 'th', 'yi', 'tl', 'id', 'ta', 'ga',
    'tt', 'it', 'te', 'is', 'tr', 'es', 'udm', 'kk', 'uz', 'kn', 'uk', 'ca', 'ur', 'ky', 'fi', 'zh', 'fr', 'ko', 'hi',
    'xh', 'hr', 'km', 'cs', 'lo', 'sv', 'la', 'gd', 'lv', 'et', 'lt', 'eo', 'lb', 'jv', 'mg', 'ja', 'ms'
]


def get_lang(text):
    if len(text.split()) > 0:
        lang = text.split()[0]
        if lang.split('-')[0] not in idiomas:
            lang = 'pt'
        if len(lang.split('-')) > 1:
            if lang.split('-')[1] not in idiomas:
                lang = 'pt'
    else:
        lang = 'pt'
    return lang


async def translate(msg):
    if msg.get('text'):
        if msg['text'].startswith('/tr ') or msg['text'] == '/tr':
            text = msg['text'][4:]
            lang = get_lang(text)
            if msg.get('reply_to_message'):
                if msg['reply_to_message'].get('text'):
                    text = msg['reply_to_message']['text']
                if msg['reply_to_message'].get('caption'):
                    text = msg['reply_to_message']['caption']
            else:
                text = text.replace(lang, '', 1).strip() if text.startswith(lang) else text

            if len(text) > 0:
                sent = await bot.sendMessage(msg['chat']['id'], 'Traduzindo...',
                                             reply_to_message_id=msg['message_id'])
                async with aiohttp.ClientSession() as session:
                    r = await session.post("https://translate.yandex.net/api/v1.5/tr.json/translate",
                                           data=dict(key=traducao, lang=lang, text=text))
                    req = await r.json()

                await bot.editMessageText((msg['chat']['id'], sent['message_id']),
                                          '''<b>Idioma:</b> {}
<b>Tradução:</b> <code>{}</code>'''.format(req['lang'], html.escape(req['text'][0])),
                                          parse_mode='HTML')

            else:
                await bot.sendMessage(msg['chat']['id'],
                                      'Uso: /tr <idioma> texto para traduzir (pode ser usado em resposta a uma mensagem).',
                                      reply_to_message_id=msg['message_id'])
            return True
