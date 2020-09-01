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

import os
import re

import aiohttp
import youtube_dl

from config import bot
from utils import pretty_size

ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s.%(ext)s', 'format': '140', 'noplaylist': True})

yt_headers = {"x-youtube-client-name": "1", "x-youtube-client-version": "2.20200827"}


async def search_yt(query):
    url_base = "https://www.youtube.com/results"
    url_yt = "https://www.youtube.com/watch?v="
    async with aiohttp.ClientSession() as session:
        r = await session.get(url_base, params=dict(search_query=query, pbj="1"), headers=yt_headers)
        page = await r.json()
    list_videos = []
    for video in page[1]["response"]["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]:
        if video.get("videoRenderer"):
            vid_id = video["videoRenderer"]["videoId"]
            title = video["videoRenderer"]["title"]["runs"][0]["text"]
            dic = {'title': title, 'url': url_yt + vid_id}
            list_videos.append(dic)
    return list_videos


async def youtube(msg):
    if msg.get('text'):

        if msg['text'].startswith('/yt '):
            res = await search_yt(msg['text'][4:])

            vids = ['{}: <a href="{}">{}</a>'.format(num + 1, i['url'], i['title']) for num, i in enumerate(res)]
            await bot.sendMessage(msg['chat']['id'], '\n'.join(vids) if vids else "Nenhum resultado foi encontrado", 'HTML',
                                      reply_to_message_id=msg['message_id'],
                                      disable_web_page_preview=True)
            return True


        elif msg['text'].split()[0] == '/ytdl':
            text = msg['text'][6:]

            if text:
                sent_id = (await bot.sendMessage(msg['chat']['id'], 'Obtendo informações do vídeo...', 'Markdown',
                                                 reply_to_message_id=msg['message_id']))['message_id']
                try:
                    if re.match(r'^(https?://)?(youtu\.be/|(m\.|www\.)?youtube\.com/watch\?v=).+', text):
                        yt = ydl.extract_info(text, download=False)
                    else:
                        yt = ydl.extract_info('ytsearch:' + text, download=False)['entries'][0]
                    for f in yt['formats']:
                        if f['format_id'] == '140':
                            fsize = f['filesize'] or 0
                    name = yt['title']
                except Exception as e:
                    return await bot.editMessageText((msg['chat']['id'], sent_id), 'Ocorreu um erro.\n\n' + str(e))
                if not fsize > 52428800:
                    if ' - ' in name:
                        performer, title = name.rsplit(' - ', 1)
                    else:
                        performer = yt.get('creator') or yt.get('uploader')
                        title = name
                    await bot.editMessageText((msg['chat']['id'], sent_id),
                                              'Baixando <code>{}</code> do YouTube...\n({})'.format(name,
                                                                                                    pretty_size(fsize)),
                                              'HTML')
                    ydl.download(['https://www.youtube.com/watch?v=' + yt['id']])
                    await bot.editMessageText((msg['chat']['id'], sent_id), 'Enviando áudio...')
                    await bot.sendChatAction(msg['chat']['id'], 'upload_document')
                    await bot.sendAudio(msg['chat']['id'], open(ydl.prepare_filename(yt), 'rb'),
                                        performer=performer,
                                        title=title,
                                        duration=yt['duration'],
                                        reply_to_message_id=msg['message_id'])
                    os.remove(ydl.prepare_filename(yt))
                    await bot.deleteMessage((msg['chat']['id'], sent_id))
                else:
                    await bot.editMessageText((msg['chat']['id'], sent_id),
                                              f'Ow, o arquivo resultante ({pretty_size(fsize)}) ultrapassa o meu limite de 50 MB')

            else:
                await bot.sendMessage(msg['chat']['id'], '*Uso:* /ytdl URL do vídeo ou nome', 'Markdown',
                                      reply_to_message_id=msg['message_id'])

            return True
