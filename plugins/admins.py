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

import json
import time

from amanobot.exception import TelegramError, NotEnoughRightsError
from amanobot.namedtuple import InlineKeyboardMarkup

from config import bot, bot_id, sudoers
from db_handler import conn, cursor


def is_admin(chat_id, user_id, reply_id=None):
    dic = {}
    cursor.execute('SELECT cached_admins FROM chats WHERE chat_id = ?', (chat_id,))
    adms = cursor.fetchone()[0]
    if adms:
        cached_admins = json.loads(adms)
    else:
        cached_admins = {'expires': 0}

    if cached_admins['expires'] > time.time():
        print('cache usado')
        adm_id = cached_admins['admins_list']
    else:
        print('cache criado')
        adms = bot.getChatAdministrators(chat_id)
        adm_id = []
        for ids in adms:
            adm_id.append(ids['user']['id'])
        cursor.execute('UPDATE chats SET cached_admins = ? WHERE chat_id = ?', (json.dumps(dict(admins_list=adm_id, expires=int(time.time())+1200)), chat_id))
        conn.commit()

    if user_id in adm_id or user_id in sudoers:
        dic['user'] = True
    else:
        dic['user'] = False

    if reply_id in adm_id:
        dic['reply'] = True
    else:
        dic['reply'] = False

    if bot_id in adm_id:
        dic['bot'] = True
    else:
        dic['bot'] = False

    return dic


def admins(msg):
    if msg.get('text'):
        if msg['text'].split()[0] == '/ban' or msg['text'].split()[0] == '!ban':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            else:
                if msg.get('reply_to_message'):
                    reply_id = msg['reply_to_message']['from']['id']
                    reply_name = msg['reply_to_message']['from']['first_name']
                elif len(msg['text'].split()) > 1:
                    u_id = msg['text'].split()[1]
                    try:
                        get = bot.getChat(u_id)
                        reply_id = get['id']
                        reply_name = get['first_name']
                    except (TelegramError, KeyError):
                        bot.sendMessage(msg['chat']['id'],
                                        'ID inválida ou desconhecida. use nesse formato: /ban ID do usuário',
                                        reply_to_message_id=msg['message_id'])
                        return
                else:
                    reply_id = None

                adm = is_admin(msg['chat']['id'], msg['from']['id'], reply_id)

                if adm['user']:
                    try:
                        int(reply_id)
                    except (TypeError, ValueError):
                        return bot.sendMessage(msg['chat']['id'], 'Responda alguém ou informe sua ID',
                                               reply_to_message_id=msg['message_id'])
                    if adm['bot']:
                        if adm['reply']:
                            bot.sendMessage(msg['chat']['id'], 'Esse aí tem admin',
                                            reply_to_message_id=msg['message_id'])
                        else:
                            bot.kickChatMember(msg['chat']['id'], reply_id)
                            bot.sendMessage(msg['chat']['id'], '{} baniu {}!'.format(
                                msg['from']['first_name'],
                                reply_name
                            ),
                                            reply_to_message_id=msg['message_id'])
                    else:
                        bot.sendMessage(msg['chat']['id'], 'Ei, eu nao tenho admin aqui',
                                        reply_to_message_id=msg['message_id'])


        elif msg['text'].split()[0] == '/kick' or msg['text'].split()[0] == '!kick':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            else:
                if msg.get('reply_to_message'):
                    reply_id = msg['reply_to_message']['from']['id']
                    reply_name = msg['reply_to_message']['from']['first_name']
                elif len(msg['text'].split()) > 1:
                    u_id = msg['text'].split()[1]
                    try:
                        get = bot.getChat(u_id)
                        reply_id = get['id']
                        reply_name = get['first_name']
                    except (TelegramError, KeyError):
                        bot.sendMessage(msg['chat']['id'],
                                        'ID inválida ou desconhecida. use nesse formato: /kick ID do usuário',
                                        reply_to_message_id=msg['message_id'])
                        return
                else:
                    reply_id = None

                adm = is_admin(msg['chat']['id'], msg['from']['id'], reply_id)

                if adm['user']:
                    try:
                        int(reply_id)
                    except (TypeError, ValueError):
                        return bot.sendMessage(msg['chat']['id'], 'Responda alguém ou informe sua ID',
                                               reply_to_message_id=msg['message_id'])
                    if adm['bot']:
                        if adm['reply']:
                            bot.sendMessage(msg['chat']['id'], 'Esse aí tem admin',
                                            reply_to_message_id=msg['message_id'])
                        else:
                            bot.unbanChatMember(msg['chat']['id'], reply_id)
                            bot.sendMessage(msg['chat']['id'], '{} kickou {}!'.format(
                                msg['from']['first_name'],
                                reply_name),
                                            reply_to_message_id=msg['message_id'])
                    else:
                        bot.sendMessage(msg['chat']['id'], 'Ei, eu nao tenho admin aqui',
                                        reply_to_message_id=msg['message_id'])


        elif msg['text'].split()[0] == '/mute' or msg['text'].split()[0] == '!mute':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            else:
                if msg.get('reply_to_message'):
                    reply_id = msg['reply_to_message']['from']['id']
                    reply_name = msg['reply_to_message']['from']['first_name']
                elif len(msg['text'].split()) > 1:
                    u_id = msg['text'].split()[1]
                    try:
                        get = bot.getChat(u_id)
                        reply_id = get['id']
                        reply_name = get['first_name']
                    except (TelegramError, KeyError):
                        bot.sendMessage(msg['chat']['id'],
                                        'ID inválida ou desconhecida. use nesse formato: /mute ID do usuário',
                                        reply_to_message_id=msg['message_id'])
                        return
                else:
                    reply_id = None

                adm = is_admin(msg['chat']['id'], msg['from']['id'], reply_id)

                if adm['user']:
                    try:
                        int(reply_id)
                    except (TypeError, ValueError):
                        return bot.sendMessage(msg['chat']['id'], 'Responda alguém ou informe sua ID',
                                               reply_to_message_id=msg['message_id'])
                    if adm['bot']:
                        if adm['reply']:
                            bot.sendMessage(msg['chat']['id'], 'Esse aí tem admin',
                                            reply_to_message_id=msg['message_id'])
                        else:
                            bot.restrictChatMember(msg['chat']['id'], reply_id)
                            bot.sendMessage(msg['chat']['id'], '{} restringiu {}!'.format(
                                msg['from']['first_name'],
                                reply_name),
                                            reply_to_message_id=msg['message_id'])
                    else:
                        bot.sendMessage(msg['chat']['id'], 'Ei, eu nao tenho admin aqui',
                                        reply_to_message_id=msg['message_id'])


        elif msg['text'].split()[0] == '/unmute' or msg['text'].split()[0] == '!unmute':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            else:
                if msg.get('reply_to_message'):
                    reply_id = msg['reply_to_message']['from']['id']
                    reply_name = msg['reply_to_message']['from']['first_name']
                elif len(msg['text'].split()) > 1:
                    u_id = msg['text'].split()[1]
                    try:
                        get = bot.getChat(u_id)
                        reply_id = get['id']
                        reply_name = get['first_name']
                    except TelegramError:
                        bot.sendMessage(msg['chat']['id'],
                                        'ID inválida ou desconhecida. use nesse formato: /unban ID do usuário',
                                        reply_to_message_id=msg['message_id'])
                        return
                else:
                    reply_id = None

                adm = is_admin(msg['chat']['id'], msg['from']['id'], reply_id)

                if adm['user']:
                    try:
                        int(reply_id)
                    except (TypeError, ValueError):
                        return bot.sendMessage(msg['chat']['id'], 'Responda alguém ou informe sua ID',
                                               reply_to_message_id=msg['message_id'])
                    if adm['bot']:
                        if adm['reply']:
                            bot.sendMessage(msg['chat']['id'], 'Esse aí tem admin',
                                            reply_to_message_id=msg['message_id'])
                        else:
                            bot.restrictChatMember(msg['chat']['id'], reply_id,
                                                   can_send_messages=True,
                                                   can_send_media_messages=True,
                                                   can_send_other_messages=True,
                                                   can_add_web_page_previews=True)
                            bot.sendMessage(msg['chat']['id'], '{} agora pode falar aqui!'.format(reply_name),
                                            reply_to_message_id=msg['message_id'])
                    else:
                        bot.sendMessage(msg['chat']['id'], 'Ei, eu nao tenho admin aqui',
                                        reply_to_message_id=msg['message_id'])


        elif msg['text'].split()[0] == '/unban' or msg['text'].split()[0] == '!unban':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            else:
                if msg.get('reply_to_message'):
                    reply_id = msg['reply_to_message']['from']['id']
                    reply_name = msg['reply_to_message']['from']['first_name']
                elif len(msg['text'].split()) > 1:
                    u_id = msg['text'].split()[1]
                    try:
                        get = bot.getChat(u_id)
                        reply_id = get['id']
                        reply_name = get['first_name']
                    except TelegramError:
                        bot.sendMessage(msg['chat']['id'],
                                        'ID inválida ou desconhecida. use nesse formato: /unban ID do usuário',
                                        reply_to_message_id=msg['message_id'])
                        return
                else:
                    reply_id = None

                adm = is_admin(msg['chat']['id'], msg['from']['id'], reply_id)

                if adm['user']:
                    try:
                        int(reply_id)
                    except (TypeError, ValueError):
                        return bot.sendMessage(msg['chat']['id'], 'Responda alguém ou informe sua ID',
                                               reply_to_message_id=msg['message_id'])
                    if adm['bot']:
                        if adm['reply']:
                            bot.sendMessage(msg['chat']['id'], 'Esse aí tem admin',
                                            reply_to_message_id=msg['message_id'])
                        else:
                            bot.unbanChatMember(msg['chat']['id'], reply_id)
                            bot.sendMessage(msg['chat']['id'], '{} desbaniu {}!'.format(
                                msg['from']['first_name'],
                                reply_name),
                                            reply_to_message_id=msg['message_id'])
                    else:
                        bot.sendMessage(msg['chat']['id'], 'Ei, eu nao tenho admin aqui',
                                        reply_to_message_id=msg['message_id'])


        elif msg['text'].split()[0] == '/pin' or msg['text'].split()[0] == '!pin':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            elif is_admin(msg['chat']['id'], msg['from']['id'])['user']:
                if msg.get('reply_to_message'):
                    bot.pinChatMessage(msg['chat']['id'], msg['reply_to_message']['message_id'])
                else:
                    bot.sendMessage(msg['chat']['id'], 'Responda a uma mensagem para eu fixar.',
                                    reply_to_message_id=msg['message_id'])


        elif msg['text'].split()[0] == '/unpin' or msg['text'].split()[0] == '!unpin':
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            elif is_admin(msg['chat']['id'], msg['from']['id'])['user']:
                bot.unpinChatMessage(msg['chat']['id'])
                bot.sendMessage(msg['chat']['id'], 'Mensagem desfixada',
                                reply_to_message_id=msg['message_id'])


        elif msg['text'].startswith('/title') or msg['text'].startswith('!title'):
            text = msg['text'][7:]
            if msg['chat']['type'] == 'private':
                bot.sendMessage(msg['chat']['id'], 'Este comando só funciona em grupos ¯\\_(ツ)_/¯')
            elif is_admin(msg['chat']['id'], msg['from']['id'])['user']:
                if text == '':
                    bot.sendMessage(msg['chat']['id'], 'Uso: /title titulo do grupo',
                                    reply_to_message_id=msg['message_id'])
                else:
                    try:
                        bot.setChatTitle(msg['chat']['id'], text)
                        bot.sendMessage(msg['chat']['id'], 'O novo título do grupo foi definido com sucesso!',
                                        reply_to_message_id=msg['message_id'])
                    except NotEnoughRightsError:
                        bot.sendMessage(msg['chat']['id'],
                                        'Eu nao tenho tenho permissão para alterar as informações do grupo',
                                        reply_to_message_id=msg['message_id'])
                    except TelegramError:
                        bot.sendMessage(msg['chat']['id'], 'Ocorreu um erro.',
                                        reply_to_message_id=msg['message_id'])


        elif msg['text'] == '/config':
            if is_admin(msg['chat']['id'], msg['from']['id'])['user']:
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='⚙️ Opções do chat', callback_data='options {}'.format(msg['chat']['id']))],
                    [dict(text='🗑 Deletar mensagem', callback_data='del_msg')]
                ])
                bot.sendMessage(msg['from']['id'], 'Menu de configuração do chat {}'.format(msg['chat']['title']),
                                reply_markup=kb)
                bot.sendMessage(msg['chat']['id'], 'Enviei um menu de configurações no seu pv.',
                                reply_to_message_id=msg['message_id'])
            return True

        elif msg['text'] == '/admdebug':
            res = is_admin(msg['chat']['id'], msg['from']['id'],
                           msg['reply_to_message']['from']['id'] if msg.get('reply_to_message') else None)
            bot.sendMessage(msg['chat']['id'], res)
            return True

    elif msg.get('data'):

        if msg['data'].startswith('options'):
            bot.answerCallbackQuery(msg['id'], 'Abrindo...')
            if is_admin(msg['data'].split()[1], msg['from']['id'])['user']:
                info = bot.getChat(msg['data'].split()[1])
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='IA', callback_data='ai')] +
                    [dict(text='None', callback_data='ai_switch {}'.format(msg['data'].split()[1]))],
                    [dict(text='« Voltar', callback_data='back {}'.format(msg['data'].split()[1]))]
                ])
                bot.editMessageText((msg['from']['id'], msg['message']['message_id']),
                                    'Opções do chat {}'.format(info['title']),
                                    reply_markup=kb)

        elif msg['data'].startswith('back'):
            info = bot.getChat(msg['data'].split()[1])
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [dict(text='⚙️ Opções do chat', callback_data='options {}'.format(msg['data'].split()[1]))],
                [dict(text='🗑 Deletar mensagem', callback_data='del_msg')]
            ])
            bot.editMessageText((msg['from']['id'], msg['message']['message_id']),
                                'Menu de configuração do chat {}'.format(info['title']),
                                reply_markup=kb)

        elif msg['data'] == 'del_msg':
            bot.deleteMessage((msg['from']['id'], msg['message']['message_id']))
