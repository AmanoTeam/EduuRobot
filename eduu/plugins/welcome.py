# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

from typing import Optional, Tuple

from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import InlineKeyboardMarkup, Message

from eduu.config import prefix
from eduu.database import db, dbc
from eduu.utils import button_parser, commands, get_format_keys, require_admin
from eduu.utils.localization import use_chat_lang
from eduu.utils.bot_error_log import logging_errors


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


@Client.on_message(
    filters.command(["welcomeformat", "start welcome_format_help"], prefix)
)
@use_chat_lang()
@logging_errors
async def welcome_format_message_help(c: Client, m: Message, strings):
    await m.reply_text(strings("welcome_format_help_msg"))

    await m.stop_propagation()


@Client.on_message(filters.command("setwelcome", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
@logging_errors
async def set_welcome_message(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        message = m.text.html.split(None, 1)[1]
        try:
            # Try to send message with default parameters
            sent = await m.reply_text(
                message.format(
                    id=m.from_user.id,
                    username=m.from_user.username,
                    mention=m.from_user.mention,
                    first_name=m.from_user.first_name,
                    # full_name and name are the same
                    full_name=m.from_user.first_name,
                    name=m.from_user.first_name,
                    # title and chat_title are the same
                    title=m.chat.title,
                    chat_title=m.chat.title,
                    count=(await c.get_chat_members_count(m.chat.id)),
                )
            )
        except (KeyError, BadRequest) as e:
            await m.reply_text(
                strings("welcome_set_error").format(
                    error=e.__class__.__name__ + ": " + str(e)
                )
            )
        else:
            set_welcome(m.chat.id, message)
            await sent.edit_text(
                strings("welcome_set_success").format(chat_title=m.chat.title)
            )
    else:
        await m.reply_text(
            strings("welcome_set_empty").format(bot_username=c.me.username),
            disable_web_page_preview=True,
        )


@Client.on_message(
    (filters.command("welcome") & ~filters.command(["welcome on", "welcome off"]))
    & filters.group
)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
@logging_errors
async def invlaid_welcome_status_arg(c: Client, m: Message, strings):
    await m.reply_text(strings("welcome_mode_invalid"))


@Client.on_message(filters.command("getwelcome", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
@logging_errors
async def getwelcomemsg(c: Client, m: Message, strings):
    welcome, welcome_enabled = get_welcome(m.chat.id)
    if welcome_enabled:
        await m.reply_text(
            strings("welcome_default") if welcome is None else welcome, parse_mode=None
        )
    else:
        await m.reply_text("None")


@Client.on_message(filters.command("welcome on", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def enable_welcome_message(c: Client, m: Message, strings):
    toggle_welcome(m.chat.id, True)
    await m.reply_text(strings("welcome_mode_enable").format(chat_title=m.chat.title))


@Client.on_message(filters.command("welcome off", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
@logging_errors
async def disable_welcome_message(c: Client, m: Message, strings):
    toggle_welcome(m.chat.id, False)
    await m.reply_text(strings("welcome_mode_disable").format(chat_title=m.chat.title))


@Client.on_message(
    filters.command(["resetwelcome", "clearwelcome"], prefix) & filters.group
)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
@logging_errors
async def reset_welcome_message(c: Client, m: Message, strings):
    set_welcome(m.chat.id, None)
    await m.reply_text(strings("welcome_reset").format(chat_title=m.chat.title))


@Client.on_message(filters.new_chat_members & filters.group)
@use_chat_lang()
@logging_errors
async def greet_new_members(c: Client, m: Message, strings):
    members = m.new_chat_members
    chat_title = m.chat.title
    first_name = ", ".join(map(lambda a: a.first_name, members))
    full_name = ", ".join(
        map(lambda a: a.first_name + " " + (a.last_name or ""), members)
    )
    user_id = ", ".join(map(lambda a: str(a.id), members))
    username = ", ".join(
        map(lambda a: "@" + a.username if a.username else a.mention, members)
    )
    mention = ", ".join(map(lambda a: a.mention, members))
    if not m.from_user.is_bot:
        welcome, welcome_enabled = get_welcome(m.chat.id)
        if welcome_enabled:
            if welcome is None:
                welcome = strings("welcome_default")

            if "count" in get_format_keys(welcome):
                count = await c.get_chat_members_count(m.chat.id)
            else:
                count = 0

            welcome = welcome.format(
                id=user_id,
                username=username,
                mention=mention,
                first_name=first_name,
                # full_name and name are the same
                full_name=full_name,
                name=full_name,
                # title and chat_title are the same
                title=chat_title,
                chat_title=chat_title,
                count=count,
            )
            welcome, welcome_buttons = button_parser(welcome)
            await m.reply_text(
                welcome,
                disable_web_page_preview=True,
                reply_markup=(
                    InlineKeyboardMarkup(welcome_buttons)
                    if len(welcome_buttons) != 0
                    else None
                ),
            )


commands.add_command("resetwelcome", "admin")
commands.add_command("setwelcome", "admin")
commands.add_command("welcome", "admin")
commands.add_command("welcomeformat", "admin")
