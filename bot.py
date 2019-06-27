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

print(r'''
 _____    _             ____       _           _
| ____|__| |_   _ _   _|  _ \ ___ | |__   ___ | |_
|  _| / _` | | | | | | | |_) / _ \| '_ \ / _ \| __|
| |__| (_| | |_| | |_| |  _ < (_) | |_) | (_) | |_
|_____\__,_|\__,_|\__,_|_| \_\___/|_.__/ \___/ \__|

Iniciando...
''')

import asyncio
import json
import html
import traceback
import amanobot.aio

from amanobot.exception import TelegramError, TooManyRequestsError, NotEnoughRightsError
from amanobot.aio.loop import MessageLoop
from colorama import Fore
from urllib3.exceptions import ReadTimeoutError

import backups
import db_handler as db
from config import bot, na_bot, enabled_plugins, logs, version, backups_chat
from utils import send_to_dogbin

ep = []
n_ep = {}

for num, i in enumerate(enabled_plugins):
    try:
        print(Fore.RESET + 'Carregando plugins... [{}/{}]'.format(num + 1, len(enabled_plugins)), end='\r')
        exec('from plugins.{0} import {0}'.format(i))
        ep.append(i)
    except Exception as erro:
        n_ep[i] = traceback.format_exc()
        print('\n' + Fore.RED + 'Erro ao carregar o plugin {}:{}'.format(i, Fore.RESET), erro)


async def handle(msg):
    for plugin in ep:
        try:
            p = await globals()[plugin](msg)
            if p:
                break
        except (TooManyRequestsError, NotEnoughRightsError, ReadTimeoutError):
            break
        except Exception as e:
            formatted_update = json.dumps(msg, indent=3)
            formatted_exc = traceback.format_exc()
            exc_url = await send_to_dogbin('Update:\n' + formatted_update + '\n\n\n\nFull Traceback:\n' + formatted_exc)
            await bot.sendMessage(logs, '''• <b>Erro:</b>
 » Plugin: <code>{plugin}</code>
 » Tipo do erro: <code>{exc_type}</code>
 » Descrição: <i>{exc_desc}</i>

- <a href="{exc_url}">Erro completo</a>'''.format(plugin=plugin, exc_type=e.__class__.__name__,
                                                  exc_desc=html.escape(e.description if isinstance(e, TelegramError) else str(e)), exc_url=exc_url),
                               parse_mode='html', disable_web_page_preview=True)


if __name__ == '__main__':

    answerer = amanobot.aio.helper.Answerer(bot)
    loop = asyncio.get_event_loop()

    print('\n\nBot iniciado! {}\n'.format(version))

    if backups_chat:
        backups.backup_service()

    loop.create_task(MessageLoop(bot, handle).run_forever())

    wr = db.get_restarted()

    if wr:
        try:
            na_bot.editMessageText(wr, 'Reiniciado com sucesso!')
        except TelegramError:
            pass
        db.del_restarted()
    else:
        na_bot.sendMessage(logs, '''Bot iniciado

Versão: {}
Plugins carregados: {}
Ocorreram erros em {} plugin(s){}'''.format(version, len(ep), len(n_ep),
                                            ': ' + (', '.join(n_ep)) if n_ep else ''))

    loop.run_forever()
