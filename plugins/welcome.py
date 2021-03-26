from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from dbh import dbc, db
from localization import use_chat_lang
from utils import require_admin


def escape_markdown(text):
    text = text.replace("[", r"\[")
    text = text.replace("_", r"\_")
    text = text.replace("*", r"\*")
    text = text.replace("`", r"\`")

    return text


def get_welcome(chat_id):
    dbc.execute(
        "SELECT welcome, welcome_enabled FROM groups WHERE chat_id = (?)", (chat_id,)
    )
    try:
        return dbc.fetchone()
    except IndexError:
        return None


def set_welcome(chat_id, welcome):
    dbc.execute("UPDATE groups SET welcome = ? WHERE chat_id = ?", (welcome, chat_id))
    db.commit()


def enable_welcome(chat_id):
    dbc.execute(
        "UPDATE groups SET welcome_enabled = ? WHERE chat_id = ?", (True, chat_id)
    )
    db.commit()


def disable_welcome(chat_id):
    dbc.execute(
        "UPDATE groups SET welcome_enabled = ? WHERE chat_id = ?", (False, chat_id)
    )
    db.commit()


@Client.on_message(filters.command("setwelcome", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def set_welcome_message(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        set_welcome(m.chat.id, m.text.split(None, 1)[1])
        await m.reply_text(
            strings("welcome_set_success").format(chat_title=m.chat.title)
        )
    else:
        await m.reply_text(strings("welcome_set_empty"))


@Client.on_message(
    (filters.command("welcome") & ~filters.command(["welcome on", "welcome off"]))
    & filters.group
)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def invlaid_welcome_status_arg(c: Client, m: Message, strings):
    enable_welcome(m.chat.id)
    await m.reply_text(strings("welcome_mode_invalid"))


@Client.on_message(filters.command("welcome on", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def enable_welcome_message(c: Client, m: Message, strings):
    enable_welcome(m.chat.id)
    await m.reply_text(strings("welcome_mode_enable").format(chat_title=m.chat.title))


@Client.on_message(filters.command("welcome off", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def disable_welcome_message(c: Client, m: Message, strings):
    disable_welcome(m.chat.id)
    await m.reply_text(strings("welcome_mode_disable").format(chat_title=m.chat.title))


@Client.on_message(
    filters.command(["resetwelcome", "clearwelcome"], prefix) & filters.group
)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def reset_welcome_message(c: Client, m: Message, strings):
    set_welcome(m.chat.id, None)
    await m.reply_text(strings("welcome_reset").format(chat_title=m.chat.title))


@Client.on_message(filters.new_chat_members & filters.group)
@use_chat_lang()
async def greet_new_members(c: Client, m: Message, strings):
    chat_title = m.chat.title
    chat_id = m.chat.id
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name or ""
    full_name = m.from_user.first_name + last_name
    user_id = m.from_user.id
    if m.from_user.is_bot:
        pass
    else:
        welcome = get_welcome(chat_id)
        if welcome[1]:
            if welcome[0] is not None:
                welcome = welcome[0].replace("$id", str(user_id))
                welcome = welcome.replace("$title", escape_markdown(chat_title))
                welcome = welcome.replace("$name", escape_markdown(full_name))
                welcome = welcome.replace("$first_name", escape_markdown(first_name))
                welcome = welcome.replace("$last_name", escape_markdown(last_name))
            else:
                welcome = strings("welcome_default").format(
                    user_name=escape_markdown(first_name),
                    chat_title=escape_markdown(chat_title),
                )
            await m.reply_text(
                welcome, parse_mode="markdown", disable_web_page_preview=True
            )
