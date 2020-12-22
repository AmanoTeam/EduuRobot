from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from utils import commands
from localization import use_chat_lang
from consts import http


@Client.on_message(filters.command("paste", prefix))
@use_chat_lang(context="pastes")
async def dogbin(c: Client, m: Message, strings):
    if m.reply_to_message:
        if m.reply_to_message.document:
            tfile = m.reply_to_message
            to_file = await tfile.download()
            with open(to_file, 'rb') as fd:
                mean = fd.read().decode('UTF-8')
        if m.reply_to_message.text:
            mean = m.reply_to_message.text

        url = "https://del.dog/documents"
        r = await http.post(url, data=mean.encode('UTF-8'))
        url = f"https://del.dog/{r.json()['key']}"
        await m.reply_text(url, disable_web_page_preview=True)
    else:
        await m.reply_text(strings("reply_to_document_or_text"))


commands.add_command("paste", "tools", "dogbin_description", context_location="pastes")
