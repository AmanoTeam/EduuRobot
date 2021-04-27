from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup

from config import prefix
from dbh import dbc, db
from localization import use_chat_lang
from utils import require_admin, commands, button_parser


def get_rules(chat_id):
    dbc.execute("SELECT rules FROM groups WHERE chat_id = (?)", (chat_id,))
    try:
        return dbc.fetchone()[0]
    except IndexError:
        return None


def set_rules(chat_id, rules):
    dbc.execute("UPDATE groups SET rules = ? WHERE chat_id = ?", (rules, chat_id))
    db.commit()


@Client.on_message(filters.command("setrules", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def settherules(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        set_rules(m.chat.id, m.text.split(None, 1)[1])
        await m.reply_text(strings("rules_set_success").format(chat_title=m.chat.title))
    else:
        await m.reply_text(strings("rules_set_empty"))


@Client.on_message(filters.command("resetrules", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def delete_rules(c: Client, m: Message, strings):
    set_rules(m.chat.id, None)
    await m.reply_text(strings("rules_deleted"))


@Client.on_message(filters.command("rules", prefix) & filters.group)
@use_chat_lang()
async def show_rules(c: Client, m: Message, strings):
    gettherules = get_rules(m.chat.id)
    rulestxt, rules_buttons = button_parser(gettherules)
    if rulestxt:
        # TODO: Send rules in private plus a toggle for that.
        await m.reply_text(
            strings("rules_message").format(chat_title=m.chat.title, rules=rulestxt),
            reply_markup=(InlineKeyboardMarkup(rules_buttons) if len(rules_buttons) != 0 else None),
        )
    else:
        await m.reply_text(strings("rules_empty"))


commands.add_command("setrules", "admin")
commands.add_command("resetrules", "admin")
commands.add_command("rules", "admin")
