from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
import telegraph
from telegraph import Telegraph, upload_file, exceptions

telegraph = Telegraph()
r = telegraph.create_account(short_name="EduuRobot")

@Client.on_message(filters.command("telegraph", prefix))
async def telegraph(c: Client, m: Message):
    if m.reply_to_message:
        if m.reply_to_message.photo or m.reply_to_message.video:
            d_file = m.reply_to_message.download()
            media_urls = upload_file(d_file)
            tele_link = "https://telegra.ph".format(media_urls[0])
            await m.reply_text(tele_link)
    else:
        await m.reply_text("Please Reply to Photo or Video")
            
    
