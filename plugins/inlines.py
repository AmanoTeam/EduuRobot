import requests
from requests import get
from amanobot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
import config
import html
from uuid import uuid4
import duckpy
from .youtube import search_yt


bot_username = config.me['username']
bot = config.bot

proxs = 'http://api.m45ter.id/proxy_grabber.php'
geo_ip = 'http://ip-api.com/json/'

def escape_definition(prox):
    for key, value in prox.items():
        if isinstance(value, str):
            prox[key] = html.escape(value)
    return prox

def inlines(msg):
    if 'query' in msg:
        first_name = msg['from']['first_name']
        user_id = msg['from']['id']
        if 'username' in msg['from']:
            username = '@'+msg['from']['username']
        else:
            username = 'nenhum'
        if msg['query'].startswith('/ip') and len(msg['query']) > 7:
            r = requests.get(geo_ip + msg['query'][4:])
            x = ''
            for i in r.json():
                x += "*{}*: `{}`\n".format(i, r.json()[i])
            articles = [InlineQueryResultArticle(
                id='a', title='Informações de '+msg['query'][4:], input_message_content=InputTextMessageContent(message_text='*Consulta*: `'+msg['query'][4:]+'`\n\n'+x, parse_mode="Markdown"))]

            bot.answerInlineQuery(msg['id'], results=articles, cache_time=60, is_personal=True)


        elif msg['query'].startswith('/echo'):
            articles = [InlineQueryResultArticle(
                id='a', title=msg['query'][6:], input_message_content=InputTextMessageContent(message_text=msg['query'][6:]))]

            bot.answerInlineQuery(msg['id'], results=articles, cache_time=60, is_personal=True)

            
        elif msg['query'].startswith('/proxy'):
            count = 50
            number = 1
            prox = get(proxs, params={
                "max": count,
                "key": config.keys['grab_proxy']
            }).json()["result"]
            if len(prox) > 0:
                articles = []
                if count + number > len(prox):
                    maxdef = len(prox)
                else:
                    maxdef = count + number
                for i in range(number - 1, maxdef - 1):
                    deftxt = prox[i]
                    deftxt = escape_definition(deftxt)
                    articles.append(InlineQueryResultArticle(
                        id=str(uuid4()), title=deftxt["country"]+' - '+deftxt["ip"]+':'+deftxt['port'], thumb_url='http://piics.ml/i/003.png', description='Last checked: '+deftxt["last_checked"], input_message_content=InputTextMessageContent(message_text=f'<b>Proxy:</b>\nPaís: {deftxt["country"]}\nIP: <code>{deftxt["ip"]}</code>\nPorta: <code>{deftxt["port"]}</code>\nChecado há: <i>{deftxt["last_checked"]}</i>', parse_mode='HTML')))

            bot.answerInlineQuery(msg['id'], results=articles, cache_time=60, is_personal=True)


        elif msg['query'].startswith('/duck'):
            count = 50
            number = 1
            search = msg['query'][6:]
            duc = duckpy.search(str(search))['results']
            articles = []
            if duc:
                if count + number > len(duc):
                    maxdef = len(duc)
                else:
                    maxdef = count + number
                for i in range(number - 1, maxdef - 1):
                        deftxt = duc[i]
                        deftxt = escape_definition(deftxt)
                        articles.append(InlineQueryResultArticle(
                                             id=str(uuid4()),
                                             title=deftxt['title'],
                                             thumb_url='http://piics.ml/i/003.png',
                                             description=deftxt['url'],
                                             input_message_content=InputTextMessageContent(
                                                 message_text=f"<b>{deftxt['title']}</b>\n{deftxt['url']}",
                                                 parse_mode='HTML')))
            else:
                articles.append(InlineQueryResultArticle(
                                     id=str(uuid4()),
                                     title="Sem resultados.",
                                     input_message_content=InputTextMessageContent(
                                         message_text=f"Sem resultados para '{search}'."
                                     )))

            bot.answerInlineQuery(msg['id'], results=articles, cache_time=60, is_personal=True)


        elif msg['query'].startswith('/invert'):
            query = msg['query'][8:]
            articles = [InlineQueryResultArticle(id='abcde', title=query[::-1],
                                                 input_message_content=InputTextMessageContent(
                                                     message_text=query[::-1]))]

            bot.answerInlineQuery(msg['id'], results=articles)


        elif msg['query'].startswith('/markdown'):
            articles = [InlineQueryResultArticle(
                id='a', title=msg['query'][10:], input_message_content=InputTextMessageContent(message_text=kk, parse_mode='Markdown'))]

            bot.answerInlineQuery(msg['id'], results=articles)


        elif msg['query'].startswith('/html'):
            articles = [InlineQueryResultArticle(
                id='a', title=msg['query'][6:], input_message_content=InputTextMessageContent(message_text=msg['query'][6:], parse_mode='html'))]

            bot.answerInlineQuery(msg['id'], results=articles)


        elif msg['query'].startswith('/yt '):
            articles = []
            search = search_yt(msg['query'][4:])
            for i in search:
                articles.append(InlineQueryResultArticle(
                    id=str(uuid4()), title=i['title'], thumb_url=f"https://i.ytimg.com/vi/{i['url'].split('v=')[1]}/default.jpg", input_message_content=InputTextMessageContent(message_text=i['url'])))
            if not articles:
                articles.append(InlineQueryResultArticle(
                        id=str(uuid4()), title=f'Nenhum resultado encontrado para "{msg["query"][4:]}".', input_message_content=InputTextMessageContent(message_text='.')))

            bot.answerInlineQuery(msg['id'], results=articles, cache_time=60, is_personal=True)


        elif msg['query'].startswith('/faces'):
            articles = [
                InlineQueryResultArticle(
                    id='a', title='¯\\_(ツ)_/¯', input_message_content=InputTextMessageContent(message_text='¯\\_(ツ)_/¯')),
                InlineQueryResultArticle(
                    id='b', title='( ͡° ͜ʖ ͡°)', input_message_content=dict(message_text='( ͡° ͜ʖ ͡°)')),
                InlineQueryResultArticle(
                    id='c', title='( ͡~ ͜ʖ ͡°)', input_message_content=dict(message_text='( ͡~ ͜ʖ ͡°)')),
                InlineQueryResultArticle(
                    id='d', title='( ͡◐ ͜ʖ ͡◑))', input_message_content=dict(message_text='( ͡◐ ͜ʖ ͡◑))')),
                InlineQueryResultArticle(
                    id='e', title='( ͡◔ ͜ʖ ͡◔)', input_message_content=dict(message_text='( ͡◔ ͜ʖ ͡◔)')),
                InlineQueryResultArticle(
                    id='f', title='( ͡⚆ ͜ʖ ͡⚆)', input_message_content=dict(message_text='( ͡⚆ ͜ʖ ͡⚆)')),
                InlineQueryResultArticle(
                    id='g', title='( ͡ʘ ͜ʖ ͡ʘ)', input_message_content=dict(message_text='( ͡ʘ ͜ʖ ͡ʘ)')),
                InlineQueryResultArticle(
                    id='h', title='ヽ༼ຈل͜ຈ༽ﾉ', input_message_content=dict(message_text='ヽ༼ຈل͜ຈ༽ﾉ')),
                InlineQueryResultArticle(
                    id='i', title='༼ʘ̚ل͜ʘ̚༽', input_message_content=dict(message_text='༼ʘ̚ل͜ʘ̚༽')),
                InlineQueryResultArticle(
                    id='j', title='(╯°□°）╯', input_message_content=dict(message_text='(╯°□°）╯')),
                InlineQueryResultArticle(
                    id='k', title='(ﾉ◕ヮ◕)ﾉ', input_message_content=dict(message_text='(ﾉ◕ヮ◕)ﾉ')),
                InlineQueryResultArticle(
                    id='l', title='(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧', input_message_content=dict(message_text='(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧')),
                InlineQueryResultArticle(
                    id='m', title='(◕‿◕)', input_message_content=dict(message_text='(◕‿◕)')),
                InlineQueryResultArticle(
                    id='n', title='(｡◕‿‿◕｡)', input_message_content=dict(message_text='(｡◕‿‿◕｡)')),
                InlineQueryResultArticle(
                    id='o', title='(っ◕‿◕)っ', input_message_content=dict(message_text='(っ◕‿◕)っ')),
                InlineQueryResultArticle(
                    id='p', title='(づ｡◕‿‿◕｡)づ', input_message_content=dict(message_text='(づ｡◕‿‿◕｡)づ')),
                InlineQueryResultArticle(
                    id='q', title='༼ つ ◕_◕ ༽つ', input_message_content=dict(message_text='༼ つ ◕_◕ ༽つ')),
                InlineQueryResultArticle(
                    id='r', title='(ง ͠° ͟ل͜ ͡°)ง', input_message_content=dict(message_text='(ง ͠° ͟ل͜ ͡°)ง')),
                InlineQueryResultArticle(
                    id='s', title='(ง\'̀-\'́)ง', input_message_content=dict(message_text='(ง\'̀-\'́)ง')),
                InlineQueryResultArticle(
                    id='t', title='ᕙ(⇀‸↼‶)ᕗ', input_message_content=dict(message_text='ᕙ(⇀‸↼‶)ᕗ')),
                InlineQueryResultArticle(
                    id='u', title='(҂⌣̀_⌣́)', input_message_content=dict(message_text='(҂⌣̀_⌣́)')),
                InlineQueryResultArticle(
                    id='v', title='ᕦ(ò_óˇ)ᕤ', input_message_content=dict(message_text='ᕦ(ò_óˇ)ᕤ')),
                InlineQueryResultArticle(
                    id='w', title='╚(ಠ_ಠ)=┐', input_message_content=dict(message_text='╚(ಠ_ಠ)=┐')),
                InlineQueryResultArticle(
                    id='x', title='ლ(ಠ益ಠლ)', input_message_content=dict(message_text='ლ(ಠ益ಠლ)')),
                InlineQueryResultArticle(
                    id='y', title='\\_(ʘ_ʘ)_/', input_message_content=dict(message_text='\\_(ʘ_ʘ)_/')),
                InlineQueryResultArticle(
                    id='z', title='( ⚆ _ ⚆ )', input_message_content=dict(message_text='( ⚆ _ ⚆ )')),
                InlineQueryResultArticle(
                    id='aa', title='(ಥ﹏ಥ)', input_message_content=dict(message_text='(ಥ﹏ಥ)')),
                InlineQueryResultArticle(
                    id='ab', title='﴾͡๏̯͡๏﴿', input_message_content=dict(message_text='﴾͡๏̯͡๏﴿')),
                InlineQueryResultArticle(
                    id='ac', title='(◔̯◔)', input_message_content=dict(message_text='(◔̯◔)')),
                InlineQueryResultArticle(
                    id='ad', title='(ಠ_ಠ)', input_message_content=dict(message_text='(ಠ_ಠ)')),
                InlineQueryResultArticle(
                    id='ae', title='(ಠ‿ಠ)', input_message_content=dict(message_text='(ಠ‿ಠ)')),
                InlineQueryResultArticle(
                    id='af', title='(¬_¬)', input_message_content=dict(message_text='(¬_¬)')),
                InlineQueryResultArticle(
                    id='ag', title='(¬‿¬)', input_message_content=dict(message_text='(¬‿¬)')),
                InlineQueryResultArticle(
                    id='ah', title='\\ (•◡•) /', input_message_content=dict(message_text='\\ (•◡•) /')),
                InlineQueryResultArticle(
                    id='ai', title='(◕‿◕✿)', input_message_content=dict(message_text='(◕‿◕✿)')),
                InlineQueryResultArticle(
                    id='aj', title='( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)', input_message_content=dict(message_text='( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)'))]

            bot.answerInlineQuery(msg['id'], results=articles)

        
        elif msg['query'].startswith('/hidemsg'):
            articles = [InlineQueryResultArticle(
                id='a', title='Resultado: '+msg['query'][9:], input_message_content=InputTextMessageContent(message_text='\u2060'*3600+msg['query'][9:]))]
            bot.answerInlineQuery(msg['id'], results=articles, cache_time=60, is_personal=True)

        else:
            articles = [
                InlineQueryResultArticle(
                    id='a', title='Informações', description='Exibe informações sobre você', input_message_content=dict(message_text='<b>Suas informações:</b>\n\n<b>Nome:</b> <code>'+html.escape(first_name)+'</code>\n<b>ID:</b> <code>'+str(user_id)+'</code>\n<b>Username:</b> <code>'+username+'</code>', parse_mode="HTML")),
                InlineQueryResultArticle(
                     id='b', title='/duck', description='searching with ddg engine', input_message_content=dict(message_text='Uso: /duck')),
                InlineQueryResultArticle(
                    id='c', title='/faces', description='Mostra uma lista de carinhas ¯\\_(ツ)_/¯', input_message_content=dict(message_text='Uso: @{} /faces - exibe uma lista de carinhas ¯\\_(ツ)_/¯'.format(bot_username))),
                InlineQueryResultArticle(
                    id='d', title='/hidemsg', description='Envia uma mensagem que não aparece nas ações recentes ao ser apagada em até 1 minuto.', input_message_content=dict(message_text='Uso: @{} /hidemsg texto para a mensagem\n\nEnvia uma mensagem que se for apagada em até 1 minuto não aparece nas ações recentes do grupo'.format(bot_username))),
                InlineQueryResultArticle(
                    id='e', title='/html', description='Formata um texto usando HTML', input_message_content=dict(message_text='Uso: @{} /html <b>texto</b>'.format(bot_username))),
                InlineQueryResultArticle(
                    id='f', title='/ip', description='Exibe informações de um IP informado', input_message_content=dict(message_text='Uso: @{} /ip google.com'.format(bot_username))),
                InlineQueryResultArticle(
                    id='g', title='/proxy', description='searching proxy', input_message_content=dict(message_text='Uso: @{} /proxy - Exibe uma lista de proxys de vários países.'.format(bot_username))),
                InlineQueryResultArticle(
                    id='h', title='/yt', description='Pesquisar vídeos no YouTube', input_message_content=dict(message_text='Uso: @{} /yt - Pesquisar vídeos no YouTube.'.format(bot_username)))
                ]

            bot.answerInlineQuery(msg['id'], results=articles, cache_time=60, is_personal=True)
