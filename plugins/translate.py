import re
import html
import base64

from googletrans import Translator, LANGUAGES
from pyrogram import Client, Filters
from config import prefix


def get_lang(text):
    if len(text.split()) > 0:
        lang = text.split()[0]
        if lang.split("-")[0] not in LANGUAGES:
            lang = "pt"
        if len(lang.split("-")) > 1:
            if lang.split("-")[1] not in LANGUAGES:
                lang = "pt"
    else:
        lang = "pt"
    return lang


@Client.on_message(Filters.command("tr", prefix))
async def translate(client, message):
    translator = Translator()
    text = message.text[4:]
    lang = get_lang(text)
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    else:
        text = text.replace(lang, "", 1).strip() if text.startswith(lang) else text

    if len(text):
        sent = await message.reply_text("Translating...",
                                        reply_to_message_id=message.message_id)
        langs = {}

        if len(lang.split("-")) > 1:
            langs["src"] = lang.split("-")[0]
            langs["dest"] = lang.split("-")[1]
        else:
            langs["dest"] = lang

        emojis = re.findall(r"[^\w\s<>,\.!\?;:\\#@'\"]+", text)

        emojisdict = {}
        for emoji in emojis:
            em = base64.b16encode(emoji.encode()).decode()
            emojisdict[em] = emoji
            text = text.replace(emoji, f"<{em}>")

        trres = translator.translate(text, **langs)
        text = trres.text

        for key in emojisdict:
            text = text.replace(f"<{key}>", emojisdict[key])

        res = html.escape(text)
        await sent.edit("""<b>Language:</b> {} -> {}
<b>Translation:</b> <code>{}</code>""".format(trres.src, trres.dest, res),
                                          parse_mode="HTML")

    else:
        await message.reply_text("Usage: /tr <language> text for translation (It can be used in reply to a message).",
                                 reply_to_message_id=message.message_id, parse_mode="md")
