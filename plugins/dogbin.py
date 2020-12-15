import requests

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix

@Client.on_message(filters.command("paste", prefix))
async def dogbin(c: Client, m: Message):
    if m.reply_to_message:
        if m.reply_to_message.document:
            tfile = m.reply_to_message
            to_file = await tfile.download()
            m_list = None
            with open(to_file,'rb') as fd:
                m_list = fd.readlines()
            mean=""
            for s in m_list:
                mean+= s.decode('UTF-8') +"\r\n"
            url = f"https://del.dog/documents"
            r = requests.post(url,data = mean.encode('UTF-8')).json()
            url = f"https://del.dog/{r['key']}"
            await m.reply_text(url,disable_web_page_preview=True)
        if m.reply_to_message.text:
            mean = m.reply_to_message.text
            url = f"https://del.dog/documents"
            r = requests.post(url,data = mean.encode('UTF-8')).json()
            url = f"https://del.dog/{r['key']}"
            await m.reply_text(url,disable_web_page_preview=True)
    else:
        await m.reply_text("Please Reply to message or document.")
