# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, Message

from config import PREFIXES
from eduu.database.rules import get_rules, set_rules
from eduu.utils import button_parser, commands
from eduu.utils.decorators import require_admin, stop_here
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command(["setrules", "defregras"], PREFIXES) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang
async def settherules(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        await set_rules(m.chat.id, m.text.split(None, 1)[1])
        await m.reply_text(strings("rules_set_success").format(chat_title=m.chat.title))
    else:
        await m.reply_text(strings("rules_set_empty"))


@Client.on_message(
    filters.command(["resetrules", "resetarregras"], PREFIXES) & filters.group
)
@require_admin(permissions=["can_change_info"])
@use_chat_lang
async def delete_rules(c: Client, m: Message, strings):
    await set_rules(m.chat.id, None)
    await m.reply_text(strings("rules_deleted"))


@Client.on_message(filters.command(["rules", "regras"], PREFIXES) & filters.group)
@use_chat_lang
async def show_rules(c: Client, m: Message, strings):
    gettherules = await get_rules(m.chat.id)
    rulestxt, rules_buttons = button_parser(gettherules)
    if rulestxt:
        await m.reply_text(
            strings("rules_message").format(chat_title=m.chat.title, rules=rulestxt),
            reply_markup=(
                InlineKeyboardMarkup(rules_buttons) if len(rules_buttons) != 0 else None
            ),
        )
    else:
        await m.reply_text(strings("rules_empty"))


@Client.on_message(filters.regex("^/start rules_") & filters.private)
@use_chat_lang
@stop_here
async def show_rules_pvt(c: Client, m: Message, strings):
    cid_one = m.text.split("_")[1]
    gettherules = await get_rules(cid_one if cid_one.startswith("-") else f"-{cid_one}")
    rulestxt, rules_buttons = button_parser(gettherules)
    if rulestxt:
        await m.reply_text(
            rulestxt,
            reply_markup=(
                InlineKeyboardMarkup(rules_buttons) if len(rules_buttons) != 0 else None
            ),
        )
    else:
        await m.reply_text(strings("rules_empty"))


commands.add_command("setrules", "admin")
commands.add_command("resetrules", "admin")
commands.add_command("rules", "admin")
