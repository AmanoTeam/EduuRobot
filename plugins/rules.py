from pyrogram import Client, filters
from pyrogram.types import Message
from dbh import dbc, db
from utils import require_admin
from config import prefix


def get_rules(chat_id):
    dbc.execute('SELECT rules FROM groups WHERE chat_id = (?)', (chat_id,))
    try:
        return dbc.fetchone()[0]
    except IndexError:
        return None


def set_rules(chat_id, rules):
    dbc.execute('UPDATE groups SET rules = ? WHERE chat_id = ?', (rules, chat_id))
    db.commit()


@Client.on_message(filters.command("setrules", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
async def settherules(c: Client, m: Message):
    set_rules(m.chat.id, m.text.split(None, 1)[1])
    await m.reply_text(f"the rules for {m.chat.title} was setted successfully")
        
@Client.on_message(filters.command("restrules", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
async def delete_rules(c: Client, m: Message):
    set_rules(m.chat.id, None)
    await m.reply_text("the rules was deleted successfully.")
 
        
@Client.on_message(filters.command("rules", prefix) & filters.group)
async def show_rules(c: Client, m: Message):
    rules = get_rules(m.chat.id) or "the rules was not setted"
    await m.reply_text(f"the rules in the chat {m.chat.title}: \n\n {rules}")
