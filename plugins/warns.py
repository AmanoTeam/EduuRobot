from pyrogram import Client, filters
from pyrogram.types import Message
from dbh import dbc, db
from utils import require_admin, time_extract, html_user, commands
from config import prefix
from .admin import get_target_user

dbc.execute('''CREATE TABLE IF NOT EXISTS user_warns (
                                                         user_id INTEGER,
                                                         chat_id INTEGER,
                                                         count INTEGER)''')


def get_warns(chat_id, user_id):
    dbc.execute('SELECT count FROM user_warns WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    return dbc.fetchone()[0]


def add_warns(chat_id, user_id, number):
    dbc.execute('SELECT * FROM user_warns WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    if dbc.fetchone():
        dbc.execute('UPDATE user_warns SET count = count + ? WHERE chat_id = ? AND user_id = ?',
                       (number, chat_id, user_id))
        db.commit()
    else:
        dbc.execute('INSERT INTO user_warns (user_id, chat_id, count) VALUES (?,?,?)', (user_id, chat_id, number))
        db.commit()
    return True


def set_warns_limit(chat_id, rules):
    cursor.execute('UPDATE chats SET rules = ? WHERE chat_id = ?', (rules, chat_id))
    conn.commit()


def reset_warns(chat_id, user_id):
    dbc.execute('DELETE FROM user_warns WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    db.commit()
    return True

@Client.on_message(filters.command("warn", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
async def warn_user(c: Client, m: Message):
    target_user = await get_target_user(c, m)
    warns_limit = 3
    add_warns(m.chat.id, target_user.id, 1)
    user_warns = get_warns(m.chat.id, target_user.id)
    if user_warns >= warns_limit:
        await c.kick_chat_member(m.chat.id, target_user.id)
        await m.reply_text(f"the user {target_user.mention} was banned because he was warned {user_warns} of {warns_limit} times")
    else:
        await m.reply(f"the user {target_user.mention} has {user_warns} of {warns_limit} warnings")
        
        
@Client.on_message(filters.command("unwarn", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
async def unwarn_user(c: Client, m: Message):
    target_user = await get_target_user(c, m)
    reset_warns(m.chat.id, target_user.id)
    await m.reply_text(f"the warns of the user {target_user.mention} was removed")
