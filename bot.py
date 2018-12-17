print(r'''
 _____    _             ____       _           _   
| ____|__| |_   _ _   _|  _ \ ___ | |__   ___ | |_ 
|  _| / _` | | | | | | | |_) / _ \| '_ \ / _ \| __|
| |__| (_| | |_| | |_| |  _ < (_) | |_) | (_) | |_ 
|_____\__,_|\__,_|\__,_|_| \_\___/|_.__/ \___/ \__|

Iniciando...
''')

import io
import sys
import threading
import time
import traceback
from contextlib import redirect_stdout

from amanobot.exception import TelegramError, TooManyRequestsError, NotEnoughRightsError
from amanobot.loop import MessageLoop
from colorama import Fore
from urllib3.exceptions import ReadTimeoutError

import config
import db_handler as db

bot = config.bot

ep = []
n_ep = []

for num, i in enumerate(config.enabled_plugins):
    try:
        print(Fore.RESET + 'Carregando plugins... [{}/{}]'.format(num + 1, len(config.enabled_plugins)), end='\r')
        exec('from plugins.{0} import {0}'.format(i))
        ep.append(i)
    except Exception as erro:
        n_ep.append(i)
        print('\n' + Fore.RED + 'Erro ao carregar o plugin {}:{}'.format(i, Fore.RESET), erro)


def handle_thread(*args):
    t = threading.Thread(target=handle, args=args)
    t.start()


def handle(msg):
    try:
        for plugin in ep:
            p = globals()[plugin](msg)
            if p:
                break
    except (TooManyRequestsError, NotEnoughRightsError, ReadTimeoutError):
        pass
    except Exception:
        with io.StringIO() as buf, redirect_stdout(buf):
            traceback.print_exc(file=sys.stdout)
            res = buf.getvalue()
        bot.sendMessage(config.logs, '''Ocorreu um erro no plugin {}:

{}'''.format(plugin, res))


print('\n\nBot iniciado! {}\n'.format(config.version))

MessageLoop(bot, handle_thread).run_as_thread()

wr = db.get_restarted()

if wr:
    try:
        bot.editMessageText(wr, 'Reiniciado com sucesso!')
    except TelegramError:
        pass
    db.del_restarted()
else:
    bot.sendMessage(config.logs, '''Bot iniciado

Versão: {}
Plugins carregados: {}
Ocorreram erros em {} plugin(s){}'''.format(config.version, len(ep), len(n_ep),
                                            ': ' + (', '.join(n_ep)) if n_ep else ''))

while True:
    time.sleep(10)
