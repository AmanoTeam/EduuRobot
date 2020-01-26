import html
import regex

from pyrogram import Client, Filters
from localization import GetLang


@Client.on_message(Filters.regex(r'^s/(.+)?/(.+)?(/.+)?') & Filters.reply)
async def sed(client, message):
    _ = GetLang(message).strs
    exp = regex.split(r'(?<![^\\]\\)/', message.text)
    pattern = exp[1]
    replace_with = exp[2].replace(r'\/', '/')
    flags = exp[3] if len(exp) > 3 else ''

    count = 1
    rflags = 0

    if 'g' in flags:
        count = 0
    if 'i' in flags and 's' in flags:
        rflags = regex.I | regex.S
    elif 'i' in flags:
        rflags = regex.I
    elif 's' in flags:
        rflags = regex.S

    text = message.reply_to_message.text or message.reply_to_message.caption

    if not text:
        return

    try:
        res = regex.sub(pattern, replace_with, text, count=count, flags=rflags, timeout=1)
    except TimeoutError:
        await message.reply_text(_("sed.regex_timeout"))
    except regex.error as e:
        await message.reply_text(str(e))
    else:
        await client.send_message(message.chat.id, f'<pre>{html.escape(res)}</pre>',
                                  reply_to_message_id=message.reply_to_message.message_id)
