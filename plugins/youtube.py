import config
import youtube_dl
import requests
import time
import os
from bs4 import BeautifulSoup as bs

bot = config.bot
ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s.%(ext)s', 'format': '140', 'noplaylist': True})


def pretty_size(size):
    units = ['B', 'KB', 'MB', 'GB']
    unit = 0
    while size >= 1024:
        size /= 1024
        unit += 1
    return '%0.2f %s' % (size, units[unit])


def search_yt(query):
    URL_BASE = "https://www.youtube.com/results"
    url_yt= "https://www.youtube.com"
    r = requests.get(URL_BASE, params=dict(search_query=query))
    page = r.text
    soup = bs(page,"html.parser")
    id_url = None
    list_videos = []
    for link in soup.find_all('a'):
        url = link.get('href')
        title = link.get('title')
        if url.startswith("/watch") and (id_url!=url) and (title!=None):
            id_url = url
            dic = {'title':title,'url':url_yt+url}
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
                    vids += '{}: <a href="{}">{}</a>\n'.format(num+1,i['url'], i['title'])
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
                        yt = ydl.extract_info('ytsearch:'+text, download=False)['entries'][0]
                    else:
                        url = text
                        yt = ydl.extract_info(url, download=False)
                    for format in yt['formats']:
                        if format['format_id'] == '140':
                            fsize = format['filesize']
                    name = yt['title']
                    extname = yt['title']+'.m4a'
                except Exception as e:
                    return bot.editMessageText(
                        (msg['chat']['id'],sent_id),
                        text='Ocorreu um erro.\n\n'+str(e)
                    )
                if fsize < 52428800:
                    first = time.time()
                    if ' - ' in name:
                        performer, title = name.rsplit(' - ',1)
                    else:
                        performer = None
                        title = name
                    bot.editMessageText((msg['chat']['id'],sent_id),
                                        'Baixando <code>{}</code> do YouTube...\n({})'.format(name,pretty_size(fsize)), 'HTML')
                    ydl.extract_info(url, download=True)
                    bot.editMessageText((msg['chat']['id'],sent_id), 'Enviando áudio...')
                    bot.sendChatAction(msg['chat']['id'], 'upload_document')
                    sent = bot.sendAudio(msg['chat']['id'], open(ydl.prepare_filename(yt), 'rb'),
                        performer=performer,
                        title=title,
                        reply_to_message_id=msg['message_id']
                    )
                    os.remove(ydl.prepare_filename(yt))
                    bot.deleteMessage((msg['chat']['id'],sent_id))
                else:
                    bot.editMessageText((msg['chat']['id'],sent_id),
                                        'Ow, o arquivo resultante ({}) ultrapassa o meu limite de 50 MB'.format(pretty_size(fsize)))