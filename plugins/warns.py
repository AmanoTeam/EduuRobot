from pyrogram import Client, filters
from pyrogram.types import Message
from dbh import dbc, db
from utils import require_admin
from config import prefix
from .admin import get_target_user

dbc.execute('''CREATE TABLE IF NOT EXISTS user_warns (user_id INTEGER,
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


def reset_warns(chat_id, user_id):
    dbc.execute('DELETE FROM user_warns WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    db.commit()


def get_warns_limit(chat_id):
    dbc.execute('SELECT warns_limit FROM groups WHERE chat_id = ?', (chat_id,))
    res = dbc.fetchone()[0]
    return 3 if res is None else res


def set_warns_limit(chat_id, warns_limit):
    dbc.execute('UPDATE groups SET warns_limit = ? WHERE chat_id = ?', (warns_limit, chat_id))
    db.commit()


@Client.on_message(filters.command("warn", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
async def warn_user(c: Client, m: Message):
    target_user = await get_target_user(c, m)
    warns_limit = get_warns_limit(m.chat.id)
    add_warns(m.chat.id, target_user.id, 1)
    user_warns = get_warns(m.chat.id, target_user.id)
    if user_warns >= warns_limit:
        await c.kick_chat_member(m.chat.id, target_user.id)
        await m.reply_text(f"The user {target_user.mention} has been banned because they were warned {user_warns} times.")
    else:
        await m.reply(f"The user {target_user.mention} has {user_warns} out of {warns_limit} warnings.")


@Client.on_message(filters.command("setwarnslimit", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members", "can_change_info"])
async def warns_limit(c: Client, m: Message):
    if len(m.command) == 1:
        return await m.reply_text("You must specify a number of warnings, E.g.: <code>/setwarnslimit 5</code>.")
    try:
        warns_limit = int(m.command[1])
    except ValueError:
        await m.reply_text("The provided value is not valid.")
    else:
        set_warns_limit(m.chat.id, warns_limit)
        await m.reply(f"Warnings limit successfully changed to {warns_limit}.")


@Client.on_message(filters.command(["resetwarns", "unwarn"], prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
async def unwarn_user(c: Client, m: Message):
    target_user = await get_target_user(c, m)
    reset_warns(m.chat.id, target_user.id)
    await m.reply_text(f"{target_user.mention} warnings were successfully removed.")
