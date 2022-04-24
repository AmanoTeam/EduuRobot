from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from eduu.config import prefix
from eduu.database import db, dbc
from eduu.utils import commands, require_admin
from eduu.utils.localization import use_chat_lang


def check_if_antichannelpin(chat_id):
    dbc.execute("SELECT antichannelpin FROM groups WHERE chat_id = ?", (chat_id,))
    res = dbc.fetchone()[0]
    return res


def toggle_antichannelpin(chat_id: int, mode: Optional[bool]):
    dbc.execute(
        "UPDATE groups SET antichannelpin = ? WHERE chat_id = ?", (mode, chat_id)
    )
    db.commit()


@Client.on_message(filters.command("antichannelpin", prefix))
@require_admin(permissions=["can_pin_messages"])
@use_chat_lang()
async def setantichannelpin(c: Client, m: Message, strings):
    if len(m.text.split()) > 1:
        if m.command[1] == "on":
            toggle_antichannelpin(m.chat.id, True)
            await m.reply_text(strings("antichannelpin_enabled"))
        elif m.command[1] == "off":
            toggle_antichannelpin(m.chat.id, None)
            await m.reply_text(strings("antichannelpin_disabled"))
        else:
            await m.reply_text(strings("antichannelpin_invalid_arg"))
    else:
        check_acp = check_if_antichannelpin(m.chat.id)
        if not check_acp:
            await m.reply_text(strings("antichannelpin_status_disabled"))
        else:
            await m.reply_text(strings("antichannelpin_status_enabled"))


@Client.on_message(filters.linked_channel, group=-1)
async def acp_action(c: Client, m: Message):
    get_acp = check_if_antichannelpin(m.chat.id)
    getmychatmember = await m.chat.get_member("me")
    if (get_acp and getmychatmember.can_pin_messages) is True:
        await m.unpin()
    else:
        pass


@Client.on_message(filters.command("pin", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def pin(c: Client, m: Message):
    disable_notifications = "loud" not in m.text

    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.id,
        disable_notification=disable_notifications,
        both_sides=True,
    )


@Client.on_message(filters.command("unpin", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def unpin(c: Client, m: Message):
    await c.unpin_chat_message(m.chat.id, m.reply_to_message.id)


@Client.on_message(filters.command(["unpinall", "unpin all"], prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def unpinall(c: Client, m: Message):
    await c.unpin_all_chat_messages(m.chat.id)


commands.add_command("antichannelpin", "admin")
commands.add_command("pin", "admin")
commands.add_command("unpin", "admin")
commands.add_command("unpinall", "admin")
