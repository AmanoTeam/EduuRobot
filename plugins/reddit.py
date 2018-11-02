import config
import requests
import re

bot = config.bot
bot_username = config.bot_username
def redddit(msg):
    if msg.get('text'):
            if msg['text'].startswith('/r ') or msg['text'].startswith('!r '):
              sub = msg['text'][3:]
              if sub:
                      sub = re.findall(r'\S*', sub)
                      sub = "r/" + sub[0] if sub[0:2] != "r/" else sub[0]
                      url = "http://www.reddit.com/" + sub + "/.json?limit=6"
                      subreddit = "http://www.reddit.com/" + sub
                      request = requests.get(url, headers={'User-agent': 'testscript by /u/fakebot3'})
                      data = request.json()
                      posts = ""
                      if request.status_code == 200:
                          for post in data['data']['children']:
                              domain = post['data']['domain']
                              title = treatTitle(post['data']['title'])
                              pUrl = urllib.parse.quote_plus(post['data']['url'])
                              isNsfw_bool = post['data']['over_18']
                              permalink = "http://www.reddit.com" + post['data']['permalink']
                              if isNsfw_bool:
                                  isNsfw = "nsfw"
                              else:
                                  isNsfw = "sfw"
                              post = u"`> `[{title}]({pUrl})` <{nsfw}> - `[comments]({permalink})\n".format(title=title,
                                                                                                            permalink=permalink,
                                                                                                            nsfw=isNsfw, pUrl=pUrl,
                                                                                                            domain=domain)
                              posts += post
                          if posts:
                              bot.sendMessage(msg['chat']['id'], u"[{sub}]({subreddit})`:`\n\n".format(sub=sub, subreddit=subreddit) + posts, reply_to_message_id=msg['message_id'], parse_mode="Markdown", disable_web_page_preview=True) 
                          else:
                              bot.sendMessage(msg['chat']['id'], u"`I couldnt find {sub}, please try again`".format(sub=sub), reply_to_message_id=msg['message_id'], parse_mode="Markdown", disable_web_page_preview=True)
                      elif request.status_code == 403:
                          bot.sendMessage(msg['chat']['id'], "`Subreddit not found, please verify your input.`", reply_to_message_id=msg['message_id'], parse_mode="Markdown")                      
                      else:
                          bot.sendMessage(msg['chat']['id'], "`There has been an error, the number {error} to be specific.`".format(error=request.status_code), reply_to_message_id=msg['message_id'], parse_mode="Markdown")                      
                  else:
                      bot.sendMessage(msg['chat']['id'], "`Follow this command with the name of a subreddit to see the top 6 posts.\nExample: /r Awww`", reply_to_message_id=msg['message_id'], parse_mode="Markdown")
