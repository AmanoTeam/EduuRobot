"""temporary solution"""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from dbh import dbc, db
from utils import require_admin


@Client.on_message(filters.command("setchatlang", prefix) & filters.group)
@require_admin()
async def testo(c: Client, m: Message):
    dbc.execute("update groups set chat_lang = ? where chat_id = ?", (m.command[1], m.chat.id))
    db.commit()
    
