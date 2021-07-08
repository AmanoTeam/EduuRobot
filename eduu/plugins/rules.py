# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, Message

from eduu.config import prefix
from eduu.database import groups
from eduu.utils import button_parser, commands, require_admin
from eduu.utils.localization import use_chat_lang


async def get_rules(chat_id: int):
    try:
        return (await groups.get(chat_id=chat_id)).rules
    except IndexError:
        return None


async def set_rules(chat_id: int, rules):
    await groups.filter(chat_id=chat_id).update(rules=rules)


@Client.on_message(filters.command("setrules", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def settherules(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        await set_rules(m.chat.id, m.text.split(None, 1)[1])
        await m.reply_text(strings("rules_set_success").format(chat_title=m.chat.title))
    else:
        await m.reply_text(strings("rules_set_empty"))


@Client.on_message(filters.command("resetrules", prefix) & filters.group)
@require_admin(permissions=["can_change_info"])
@use_chat_lang()
async def delete_rules(c: Client, m: Message, strings):
    await set_rules(m.chat.id, None)
    await m.reply_text(strings("rules_deleted"))


@Client.on_message(filters.command("rules", prefix) & filters.group)
@use_chat_lang()
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
@use_chat_lang()
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

    await m.stop_propagation()


commands.add_command("setrules", "admin")
commands.add_command("resetrules", "admin")
commands.add_command("rules", "admin")
