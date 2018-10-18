print(r'''
 _____    _             ____       _           _   
| ____|__| |_   _ _   _|  _ \ ___ | |__   ___ | |_ 
|  _| / _` | | | | | | | |_) / _ \| '_ \ / _ \| __|
| |__| (_| | |_| | |_| |  _ < (_) | |_) | (_) | |_ 
|_____\__,_|\__,_|\__,_|_| \_\___/|_.__/ \___/ \__|

Iniciando...
''')

from amanobot.loop import MessageLoop
from colorama import Fore
import config
import time
import threading
from amanobot.exception import TooManyRequestsError, NotEnoughRightsError
from urllib3.exceptions import ReadTimeoutError
import db_handler as db


bot = config.bot

ep = []
n_ep = []


for i in config.enabled_plugins:
    try:
        print(Fore.RESET + 'Carregando plugin {}...  '.format(i), end='', flush=True)
        exec('from plugins import {0}'.format(i))
        ep.append(i)
        print(Fore.LIGHTGREEN_EX + 'Pronto!'.format(i))
    except Exception as erro:
        n_ep.append(i)
        print(Fore.LIGHTRED_EX + 'Erro!' + Fore.RESET, erro)


def handle_thread(*args):
    t = threading.Thread(target=handle, args=args)
    t.start()


def handle(msg):
    try:
        for plugin in ep:
            p = eval('{0}.{0}(msg)'.format(plugin))
            if p:
                break
    except (TooManyRequestsError, NotEnoughRightsError, ReadTimeoutError):
        pass
    except Exception as e:
        bot.sendMessage(config.logs, '''Ocorreu um erro no plugin {}:

{}: {}'''.format(plugin, type(e).__name__, e))
        raise


print(Fore.RESET + '\nBot iniciado! {}\n'.format(config.version))

MessageLoop(bot, handle_thread).run_as_thread()

wr = db.get_restarted()

if wr: 
    try:
        bot.editMessageText(wr, 'Reiniciado com sucesso!')
    except:
        pass
    db.del_restarted()
else:
    bot.sendMessage(config.logs, '''Bot iniciado

Versão: {}
Plugins carregados: {}
Ocorreram erros em {} plugin(s)'''.format(config.version, len(ep), len(n_ep)))

while True:
    time.sleep(10)
