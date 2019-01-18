from config import bot, version, bot_username
from amanobot.namedtuple import InlineKeyboardMarkup
from get_strings import strings, Strings
import keyboard


def start(msg):
    if msg.get('text'):
        strs = Strings(msg['chat']['id'])

        if msg['text'] == '/start' or msg['text'] == '!start' or msg['text'].split()[
            0] == '/start@' + bot_username:

            if msg['chat']['type'] == 'private':
                kb = keyboard.start_pv
                smsg = strs.get('pm_start_msg')
            else:
                kb = keyboard.start
                smsg = strs.get('start_msg')

            bot.sendMessage(msg['chat']['id'], smsg,
                            reply_to_message_id=msg['message_id'], reply_markup=kb)
            return True


    elif msg.get('data'):

        if msg['data'] == 'tools_cmds':
            bot.editMessageText(
                (msg['message']['chat']['id'], msg['message']['message_id']),
                text='''*Ferramentas:*

/clima - Exibe informações de clima.
/coub - Pesquisa de pequenas animações.
/echo - Repete o texto informado.
/gif - Pesquisa de GIFs.
/git - Envia informações de um user do GitHub.
/html - Repete o texto informado usando HTML.
/ip - Exibe informações sobre um IP/domínio.
/jsondump - Envia o json da mensagem.
/mark - Repete o texto informado usando Markdown.
/print - Envia uma print de um site.
/pypi - Pesquisa de módulos no PyPI.
/r - Pesquisa de tópicos no Reddit
/request - Faz uma requisição a um site.
/shorten - Encurta uma URL.
/token - Exibe informações de um token de bot.
/tr - Traduz um texto.
/yt - Pesquisa vídeos no YouTube.
/ytdl - Baixa o áudio de um vídeo no YouTube.''',
                parse_mode='Markdown',
                reply_markup=keyboard.cmds_back
            )


        elif msg['data'] == 'admin_cmds':
            bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                '''*Comandos administrativos:*

/ban - Bane um usuário.
/config - Envia um menu de configurações.
/defregras - Define as regras do grupo.
/kick - Kicka um usuário.
/mute - Restringe um usuário.
/pin - Fixa uma mensagem no grupo.
/title - Define o título do grupo.
/unban - Desbane um usuário.
/unmute - Desrestringe um usuário.
/unpin - Desfixa a mensagem fixada no grupo.
/unwarn - Remove as advertências do usuário.
/warn - Adverte um usuário.
/welcome - Define a mensagem de welcome.''',
                                parse_mode='Markdown',
                                reply_markup=keyboard.cmds_back)


        elif msg['data'] == 'user_cmds':
            bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                '''*Comandos para usuários normais:*

/add - Envia uma sugestão para a IA do bot.
/admins - Mostra a lista de admins do chat.
/dados - Envia um número aleatório de 1 a 6.
/erro - Reporta um bug ao meu desenvolvedor.
/id - Exibe suas informações ou de um usuário.
/ping - Responde com uma mensagem de ping.
/regras - Exibe as regras do grupo.
/roleta - Para jogar a Roleta Russa.''',
                                parse_mode='Markdown',
                                reply_markup=keyboard.cmds_back)


        elif msg['data'] == 'start_back':
            bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                "Olá! eu sou o EduuRobot, para descobrir mais sobre minhas funções navegue pelo teclado abaixo:",
                                reply_markup=keyboard.start_pv)


        elif msg['data'] == 'change_lang':
            langs_kb = InlineKeyboardMarkup(inline_keyboard=
                [[dict(text='{lang_flag} {lang_name}'.format(**strings[x]), callback_data='set_lang '+x)] for x in strings]+
                [[dict(text='<< Back', callback_data='start_back')]]
            )
            bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                "Select your prefered lang below:",
                                reply_markup=langs_kb)


        elif msg['data'] == 'all_cmds':
            bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                'Selecione uma categoria de comando para visualizar.\n\nCaso precise de ajuda com o bot ou tem alguma sugestão entre no @AmanoChat',
                                reply_markup=keyboard.all_cmds)


        elif msg['data'] == 'infos':
            bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                '''• EduuRobot

Version: {}
Developers: <a href="https://github.com/AmanoTeam">Amano Team</>
Owner: <a href="tg://user?id=123892996">Edu :3</>

Partnerships:
 » <a href="https://t.me/hpxlist">HPXList - by usernein</>

©2019 - <a href="https://amanoteam.ml">AmanoTeam™</>'''.format(version),
                                parse_mode='html',
                                reply_markup=keyboard.start_back,
                                disable_web_page_preview=True)
