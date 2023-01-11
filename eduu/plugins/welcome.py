# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import BadRequest
from pyrogram.types import InlineKeyboardMarkup, Message

from config import PREFIXES

from ..database.welcome import get_welcome, set_welcome, toggle_welcome
from ..utils import button_parser, commands, get_format_keys
from ..utils.decorators import require_admin
from ..utils.localization import use_chat_lang


@Client.on_message(
    filters.command(["welcomeformat", "start welcome_format_help"], PREFIXES)
)
@use_chat_lang()
async def welcome_format_message_help(c: Client, m: Message, strings):
    await m.reply_text(strings("welcome_format_help_msg"))

    await m.stop_propagation()


@Client.on_message(filters.command("setwelcome", PREFIXES) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
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
                    full_name=m.from_user.full_name,
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
                    error=f"{e.__class__.__name__}: {str(e)}"
                )
            )

        else:
            await set_welcome(m.chat.id, message)
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
async def invlaid_welcome_status_arg(c: Client, m: Message, strings):
    await m.reply_text(strings("welcome_mode_invalid"))


@Client.on_message(filters.command("getwelcome", PREFIXES) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def getwelcomemsg(c: Client, m: Message, strings):
    welcome, welcome_enabled = await get_welcome(m.chat.id)
    if welcome_enabled:
        await m.reply_text(
            strings("welcome_default") if welcome is None else welcome,
            parse_mode=ParseMode.DISABLED,
        )
    else:
        await m.reply_text("None")


@Client.on_message(filters.command("welcome on", PREFIXES) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def enable_welcome_message(c: Client, m: Message, strings):
    await toggle_welcome(m.chat.id, True)
    await m.reply_text(strings("welcome_mode_enable").format(chat_title=m.chat.title))


@Client.on_message(filters.command("welcome off", PREFIXES) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def disable_welcome_message(c: Client, m: Message, strings):
    await toggle_welcome(m.chat.id, False)
    await m.reply_text(strings("welcome_mode_disable").format(chat_title=m.chat.title))


@Client.on_message(
    filters.command(["resetwelcome", "clearwelcome"], PREFIXES) & filters.group
)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def reset_welcome_message(c: Client, m: Message, strings):
    await set_welcome(m.chat.id, None)
    await m.reply_text(strings("welcome_reset").format(chat_title=m.chat.title))


@Client.on_message(filters.new_chat_members & filters.group)
@use_chat_lang()
async def greet_new_members(c: Client, m: Message, strings):
    if m.from_user.is_bot:
        return
    welcome, welcome_enabled = await get_welcome(m.chat.id)
    members = m.new_chat_members
    mention = ", ".join(map(lambda a: a.mention, members))
    username = ", ".join(
        map(lambda a: f"@{a.username}" if a.username else a.mention, members)
    )

    user_id = ", ".join(map(lambda a: str(a.id), members))
    full_name = ", ".join(
        map(lambda a: f"{a.first_name} " + ((a.last_name or "")), members)
    )

    first_name = ", ".join(map(lambda a: a.first_name, members))
    if welcome_enabled:
        if welcome is None:
            welcome = strings("welcome_default")

        if "count" in get_format_keys(welcome):
            count = await c.get_chat_members_count(m.chat.id)
        else:
            count = 0

        chat_title = m.chat.title
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
