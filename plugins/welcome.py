from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from dbh import dbc, db
from utils import require_admin


def escape_markdown(text):
    text = text.replace('[', '\[')
    text = text.replace('_', '\_')
    text = text.replace('*', '\*')
    text = text.replace('`', '\`')

    return text
    

def get_welcome(chat_id):
    dbc.execute('SELECT welcome, welcome_enabled FROM groups WHERE chat_id = (?)', (chat_id,))
    try:
        return dbc.fetchone()
    except IndexError:
        return None


def set_welcome(chat_id, welcome):
    dbc.execute('UPDATE groups SET welcome = ? WHERE chat_id = ?', (welcome, chat_id))
    db.commit()


def enable_welcome(chat_id):
    dbc.execute('UPDATE groups SET welcome_enabled = ? WHERE chat_id = ?', (True, chat_id))
    db.commit()


def disable_welcome(chat_id):
    dbc.execute('UPDATE groups SET welcome_enabled = ? WHERE chat_id = ?', (False, chat_id))
    db.commit()


@Client.on_message(filters.command("setwelcome", prefix) & filters.group)
@require_admin()
async def set_welcome_message(c: Client, m: Message):
    if len(m.text.split()) > 1:
        set_welcome(m.chat.id, m.text.split(None, 1)[1])
        await m.reply_text(f"The welcome message for {m.chat.title} were set successfully")
    else:
        await m.reply_text("You must specify the welcome message, E.g.: <code>/setwelcome (here the welcome message)</code>.")


@Client.on_message((filters.regex(r"(?i)^/welcome$") | filters.regex(r"(?i)^!welcome$")) & filters.group)
@require_admin()
async def invlaid_welcome_status_arg(c: Client, m: Message):
    enable_welcome(m.chat.id)
    await m.reply_text("invalid argument use <code>/welcome off/on</code>.")


@Client.on_message(filters.command("welcome on", prefix) & filters.group)
@require_admin()
async def enable_welcome_message(c: Client, m: Message):
    enable_welcome(m.chat.id)
    await m.reply_text(f"the welcome message for {m.chat.title} was enabled")


@Client.on_message(filters.command("welcome off", prefix) & filters.group)
@require_admin()
async def disable_welcome_message(c: Client, m: Message):
    disable_welcome(m.chat.id)
    await m.reply_text(f"the welcome message for {m.chat.title} was disabled")

@Client.on_message(filters.command(["resetwelcome", "clearwelcome"], prefix) & filters.group)
@require_admin()
async def reset_welcome_message(c: Client, m: Message):
    set_welcome(m.chat.id, None)
    await m.reply_text(f"The welcome message for {m.chat.title} were setted again to the default welcome message of the bot.")


@Client.on_message(filters.new_chat_members & filters.group)
async def greet_new_members(c: Client, m: Message):
    chat_title = m.chat.title
    chat_id = m.chat.id
    first_name = m.from_user.first_name
    user_id = m.from_user.id
    getme = await c.get_me()
    if m.from_user.id == getme.id:
       pass
    else:
        welcome = get_welcome(chat_id)
        if welcome[1]:
            if welcome[0] is not None:
                welcome = welcome[0].replace('$id', str(user_id))
                welcome = welcome.replace('$title', escape_markdown(chat_title))
                welcome = welcome.replace('$name', escape_markdown(first_name))
            else:
                welcome = 'hey {}, welcome to {}!'.format(escape_markdown(first_name),
                                                                        escape_markdown(chat_title))
            await m.reply_text(welcome, parse_mode="markdown", disable_web_page_preview=True)
