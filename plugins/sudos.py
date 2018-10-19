import config
import os
import requests
import sys
import re
import time
import zipfile
import threading
import subprocess
import json
import html
import io
from contextlib import redirect_stdout
import db_handler as db

bot = config.bot
bot_id = config.bot_id
bot_username = config.bot_username
git_repo = config.git_repo
sudoers = config.sudoers

def sudos(msg):
    global db

    if msg.get('text'):
        if msg['from']['id'] in sudoers:

            if msg['text'] == '!sudos' or msg['text'] == '/sudos':
                bot.sendMessage(msg['chat']['id'], '''*Lista de sudos:*

*!backup* - Faz backup do bot.
*!cmd* - Executa um comando.
*!chat* - Obtem infos de um chat.
*!eval* - Executa um código Python.
*!leave* - O bot sai do chat.
*!promote* - Promove alguém a admin.
*!promoteme* - Promove você a admin.
*!restart* - Reinicia o bot.''',
                                'Markdown',
                                reply_to_message_id=msg['message_id'])
                return True


            elif msg['text'].split()[0] == '!eval':
                text = msg['text'][6:]
                try:
                    res = eval(text)
                except Exception as e:
                    res = 'Erro:\n{}: {}'.format(type(e).__name__, e)
                if res == '':
                    res == 'Código sem retornos.'
                try:
                    bot.sendMessage(msg['chat']['id'], str(res), reply_to_message_id=msg['message_id'])
                except Exception as e:
                    bot.sendMessage(msg['chat']['id'], str(e), reply_to_message_id=msg['message_id'])
                return True


            elif msg['text'] == '!restart' or msg['text'] == '!restart @' + bot_username:
                sent = bot.sendMessage(msg['chat']['id'], 'Reiniciando...',
                                       reply_to_message_id=msg['message_id'])
                db.set_restarted(sent['chat']['id'], sent['message_id'])
                time.sleep(3)
                os.execl(sys.executable, sys.executable, *sys.argv)
                del threading.Thread


            elif msg['text'].split()[0] == '!cmd':
                text = msg['text'][5:]
                if re.match('(?i).*poweroff|halt|shutdown|reboot', text):
                    res = 'Comando proibido.'
                else:
                    res = subprocess.getoutput(text)
                bot.sendMessage(msg['chat']['id'], res, reply_to_message_id=msg['message_id'])
                return True


            elif msg['text'].split()[0] == '!py':
                text = msg['text'][4:]
                try:
                    with io.StringIO() as buf, redirect_stdout(buf):
                        exec(text)
                        res = buf.getvalue()
                except Exception as e:
                    res = 'Erro: {}: {}'.format(type(e).__name__, e)
                if len(res) < 1:
                    res = 'Código sem retornos.' 
                bot.sendMessage(msg['chat']['id'], res, reply_to_message_id=msg['message_id'])
                return True


            elif msg['text'] == '!upgrade':
                sent = bot.sendMessage(msg['chat']['id'], 'Atualizando a base do bot de {}...'.format(git_repo),
                                       reply_to_message_id=msg['message_id'], disable_web_page_preview=True)
                config = open('config.py').read()
                db = open('bot.db', 'rb').read()
                os.remove('*')

                


            elif msg['text'].startswith('!leave'):
                if ' ' in msg['text']:
                    chat_id = text.split()[1]
                else:
                    chat_id = msg['chat']['id']
                if user_id in sudos:
                    bot.sendMessage(
                        chat_id=chat_id,
                        text='Tou saindo daqui flws',
                    )
                    bot.leaveChat(
                        chat_id=chat_id,
                    )


            elif msg['text'].startswith('!chat'):
                if ' ' in msg['text']:
                    chat = msg['text'].split()[1]
                else:
                    chat = msg['chat']['id']
                sent = bot.sendMessage(
                    chat_id=msg['chat']['id'],
                    text='⏰ Obtendo informações do chat...',
                    reply_to_message_id=msg['message_id']
                )['message_id']
                try:
                    res_chat = bot.getChat(chat)
                except TelegramError:
                    bot.editMessageText(
                        (chat_id, sent),
                        text='Chat não encontrado'
                    )
                if res_chat['type'] != 'private':
                    try:
                        link = bot.exportChatInviteLink(chat)
                    except:
                        link = 'Não disponível'
                    try:
                        members = bot.getChatMembersCount(chat)
                    except:
                        members = 'erro'
                    try:
                        username = '@' + res_chat['username']
                    except:
                        username = 'nenhum'
                    bot.editMessageText(
                        (msg['chat']['id'], sent),
                        text='''
<b>Informações do chat:</b>

<b>Título:</b> {}
<b>Username:</b> {}
<b>ID:</b> {}
<b>Link:</b> {}
<b>Membros:</b> {}
'''.format(html.escape(res_chat['title']), username, res_chat['id'], link, members),
                        parse_mode='HTML',
                        disable_web_page_preview=True)
                else:
                    try:
                        username = '@' + res_chat['username']
                    except:
                        username = 'nenhum'
                    bot.editMessageText(
                        (msg['chat']['id'], sent),
                        text='''
<b>Informações do chat:</b>

<b>Nome:</b> {}
<b>Username:</b> {}
<b>ID:</b> {}
'''.format(html.escape(res_chat['first_name']), username, res_chat['id']),
                        parse_mode='HTML',
                        disable_web_page_preview=True)


            elif msg['text'] == '!promoteme':
                for perms in bot.getChatAdministrators(msg['chat']['id']):
                    if perms['user']['id'] == bot_id:
                        bot.promoteChatMember(
                            chat_id=msg['chat']['id'],
                            user_id=msg['from']['id'],
                            can_change_info=perms['can_change_info'],
                            can_delete_messages=perms['can_delete_messages'],
                            can_invite_users=perms['can_invite_users'],
                            can_restrict_members=perms['can_restrict_members'],
                            can_pin_messages=perms['can_pin_messages'],
                            can_promote_members=True)


            elif msg['text'] == '!promote':
                if 'reply_to_message' in msg:
                    reply_id = msg['reply_to_message']['from']['id']
                else:
                    return
                for perms in bot.getChatAdministrators(chat_id):
                    if perms['user']['id'] == bot_id:
                        bot.promoteChatMember(
                            chat_id=msg['chat']['id'],
                            user_id=reply_id,
                            can_change_info=perms['can_change_info'],
                            can_delete_messages=perms['can_delete_messages'],
                            can_invite_users=perms['can_invite_users'],
                            can_restrict_members=perms['can_restrict_members'],
                            can_pin_messages=perms['can_pin_messages'],
                            can_promote_members=True)


            elif msg['text'].split()[0] == '!backup':
                ctime = int(time.time())

                sent = bot.sendMessage(msg['chat']['id'], '⏰ Fazendo backup...', reply_to_message_id=msg['message_id'])

                if 'pv' in msg['text'].lower() or 'privado' in msg['text'].lower():
                    msg['chat']['id'] = msg['from']['id']

                with zipfile.ZipFile('backup-{}.zip'.format(ctime), 'w', zipfile.ZIP_DEFLATED) as backup:
                    for folder, subfolders, files in os.walk('.'):
                        for file in files:
                            if file != 'backup-{}.zip'.format(ctime) and not file.endswith('.pyc'):
                                backup.write(os.path.join(folder, file))

                bot.sendDocument(msg['chat']['id'], open('backup-{}.zip'.format(ctime), 'rb'))
                bot.editMessageText((sent['chat']['id'], sent['message_id']), '✅ Backup concluído!')
                os.remove('backup-{}.zip'.format(ctime))

                return True
