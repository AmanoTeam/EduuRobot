from amanobot.namedtuple import InlineKeyboardMarkup
import config
import requests
import re
import html

bot = config.bot
bot_username = config.bot_username


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition


def pypi(msg):
    if msg.get('text'):
        if msg['text'].startswith('/pypi ') or msg['text'].startswith('!pypi '):
            text = msg['text'][6:]
            r = requests.get(f"https://pypi.python.org/pypi/{text}/json", headers={"User-Agent": "Eduu/v1.0_Beta"})
            if r.ok:
                pypi = escape_definition(r.json()["info"])
                MESSAGE = "<b>%s</b> by <i>%s</i> (%s)\n" \
                          "Platform: <b>%s</b>\n" \
                          "Version: <b>%s</b>\n" \
                          "License: <b>%s</b>\n" \
                          "Summary: <b>%s</b>\n" % (
                          pypi["name"], pypi["author"], pypi["author_email"], pypi["platform"],
                          pypi["version"], pypi["platform"], pypi["summary"])
                return bot.sendMessage(msg['chat']['id'], MESSAGE, reply_to_message_id=msg['message_id'],
                                       parse_mode="HTML", disable_web_page_preview=True,
                                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                           [dict(text='Package home page', url='{}'.format(pypi['home_page']))]]))
            else:
                return bot.sendMessage(msg['chat']['id'], f"Cant find *{text}* in pypi",
                                       reply_to_message_id=msg['message_id'], parse_mode="Markdown",
                                       disable_web_page_preview=True)
