
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

import os

import requests
import youtube_dl
from bs4 import BeautifulSoup

from config import bot

ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s.%(ext)s', 'format': '140', 'noplaylist': True})


def pretty_size(size):
    units = ['B', 'KB', 'MB', 'GB']
    unit = 0
    while size >= 1024:
        size /= 1024
        unit += 1
    return '%0.2f %s' % (size, units[unit])


def search_yt(query):
    url_base = "https://www.youtube.com/results"
    url_yt = "https://www.youtube.com"
    r = requests.get(url_base, params=dict(search_query=query))
    page = r.text
    soup = BeautifulSoup(page, "html.parser")
    id_url = None
    list_videos = []
    for link in soup.find_all('a'):
        url = link.get('href')
        title = link.get('title')
        if url.startswith("/watch") and (id_url != url) and (title is not None):
            id_url = url
            dic = {'title': title, 'url': url_yt + url}
            list_videos.append(dic)
        else:
            pass
    return list_videos


def youtube(msg):
    if msg.get('text'):

        if msg['text'].startswith('/yt '):
            try:
                res = search_yt(msg['text'][4:])
                vids = ''
                for num, i in enumerate(res):
                    vids += '{}: <a href="{}">{}</a>\n'.format(num + 1, i['url'], i['title'])
            except IndexError:
                vids = "Nenhum resultado foi encontrado"

            bot.sendMessage(msg['chat']['id'], vids, 'HTML',
                            reply_to_message_id=msg['message_id'],
                            disable_web_page_preview=True)


        elif msg['text'].startswith('/ytdl '):
            text = msg['text'][6:]

            if text == '':
                bot.sendMessage(msg['chat']['id'], '*Uso:* /ytdl URL do vídeo ou nome', 'Markdown',
                                reply_to_message_id=msg['message_id'])
            else:
                sent_id = bot.sendMessage(msg['chat']['id'], 'Obtendo informações do vídeo...', 'Markdown',
                                          reply_to_message_id=msg['message_id'])['message_id']
                try:
                    if 'youtu.be' not in text and 'youtube.com' not in text:
                        yt = ydl.extract_info('ytsearch:' + text, download=False)['entries'][0]
                    else:
                        yt = ydl.extract_info(text, download=False)
                    for f in yt['formats']:
                        if f['format_id'] == '140':
                            fsize = f['filesize']
                    name = yt['title']
                except Exception as e:
                    return bot.editMessageText(
                        (msg['chat']['id'], sent_id),
                        text='Ocorreu um erro.\n\n' + str(e)
                    )
                if fsize < 52428800:
                    if ' - ' in name:
                        performer, title = name.rsplit(' - ', 1)
                    else:
                        performer = None
                        title = name
                    bot.editMessageText((msg['chat']['id'], sent_id),
                                        'Baixando <code>{}</code> do YouTube...\n({})'.format(name, pretty_size(fsize)),
                                        'HTML')
                    ydl.extract_info('https://www.youtube.com/watch?v=' + yt['id'], download=True)
                    bot.editMessageText((msg['chat']['id'], sent_id), 'Enviando áudio...')
                    bot.sendChatAction(msg['chat']['id'], 'upload_document')
                    bot.sendAudio(msg['chat']['id'], open(ydl.prepare_filename(yt), 'rb'),
                                  performer=performer,
                                  title=title,
                                  duration=yt['duration'],
                                  reply_to_message_id=msg['message_id']
                                  )
                    os.remove(ydl.prepare_filename(yt))
                    bot.deleteMessage((msg['chat']['id'], sent_id))
                else:
                    bot.editMessageText((msg['chat']['id'], sent_id),
                                        'Ow, o arquivo resultante ({}) ultrapassa o meu limite de 50 MB'.format(
                                            pretty_size(fsize)))
