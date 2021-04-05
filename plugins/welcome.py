from typing import Optional, Tuple

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from dbh import dbc, db
from localization import use_chat_lang
from utils import require_admin, commands


def get_welcome(chat_id: int) -> Tuple[Optional[str], bool]:
    dbc.execute(
        "SELECT welcome, welcome_enabled FROM groups WHERE chat_id = (?)", (chat_id,)
    )
    return dbc.fetchone()


def set_welcome(chat_id: int, welcome: Optional[str]):
    dbc.execute("UPDATE groups SET welcome = ? WHERE chat_id = ?", (welcome, chat_id))
    db.commit()


def toggle_welcome(chat_id: int, mode: bool):
    dbc.execute(
        "UPDATE groups SET welcome_enabled = ? WHERE chat_id = ?", (mode, chat_id)
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
    await m.reply_text(strings("welcome_mode_invalid"))


@Client.on_message(filters.command("welcome on", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def enable_welcome_message(c: Client, m: Message, strings):
    toggle_welcome(m.chat.id, True)
    await m.reply_text(strings("welcome_mode_enable").format(chat_title=m.chat.title))


@Client.on_message(filters.command("welcome off", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def disable_welcome_message(c: Client, m: Message, strings):
    toggle_welcome(m.chat.id, False)
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
    if not m.from_user.is_bot:
        welcome, welcome_enabled = get_welcome(chat_id)
        if welcome_enabled:
            if welcome is not None:
                welcome = welcome.replace("$id", str(user_id))
                welcome = welcome.replace("$title", chat_title)
                welcome = welcome.replace("$name", full_name)
                welcome = welcome.replace("$first_name", first_name)
                welcome = welcome.replace("$last_name", last_name)
            else:
                welcome = strings("welcome_default").format(
                    user_name=first_name,
                    chat_title=chat_title,
                )
            await m.reply_text(
                welcome, parse_mode="markdown", disable_web_page_preview=True
            )


commands.add_command("resetwelcome", "admin")
commands.add_command("setwelcome", "admin")
commands.add_command("welcome", "admin")
