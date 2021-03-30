import asyncio

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message, User
from typing import Optional, Tuple
from config import prefix
from localization import use_chat_lang
from utils import require_admin, time_extract, commands
from dbh import dbc, db


def check_if_antichannelpin(chat_id):
    dbc.execute("SELECT antichannelpin FROM groups WHERE chat_id = ?", (chat_id,))
    res = dbc.fetchone()[0]
    return None if res is None else res


def toggle_antichannelpin(chat_id: int, mode: bool):
    dbc.execute(
        "UPDATE groups SET antichannelpin = ? WHERE chat_id = ?", (mode, chat_id)
    )
    db.commit()


async def get_target_user(c: Client, m: Message) -> User:
    if m.reply_to_message:
        target_user = m.reply_to_message.from_user
    else:
        target_user = await c.get_users(
            int(m.command[1]) if m.command[1].isdecimal() else m.command[1]
        )
    return target_user


@Client.on_message(filters.command("pin", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def pin(c: Client, m: Message):
    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id,
        disable_notification=True,
        both_sides=True,
    )


@Client.on_message(filters.command("pin loud", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def pinloud(c: Client, m: Message):
    await c.pin_chat_message(
        m.chat.id,
        m.reply_to_message.message_id,
        disable_notification=False,
        both_sides=True,
    )


@Client.on_message(filters.command("unpin", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def unpin(c: Client, m: Message):
    await c.unpin_chat_message(m.chat.id, m.reply_to_message.message_id)


@Client.on_message(filters.command("unpinall", prefix))
@require_admin(permissions=["can_pin_messages"], allow_in_private=True)
async def unpinall(c: Client, m: Message):
    await c.unpin_all_chat_messages(m.chat.id)


@Client.on_message(filters.command("ban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def ban(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)

    await c.kick_chat_member(m.chat.id, target_user.id)
    await m.reply_text(
        strings("ban_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
    )


@Client.on_message(filters.command("kick", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def kick(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)

    await c.kick_chat_member(m.chat.id, target_user.id)
    await m.chat.unban_member(target_user.id)
    await m.reply_text(
        strings("kick_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
    )


@Client.on_message(filters.command("unban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def unban(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)

    await m.chat.unban_member(target_user.id)
    await m.reply_text(
        strings("unban_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
    )


@Client.on_message(filters.command("mute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def mute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)

    await c.restrict_chat_member(
        m.chat.id, target_user.id, ChatPermissions(can_send_messages=False)
    )
    await m.reply_text(
        strings("mute_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
    )


@Client.on_message(filters.command("unmute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def unmute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)

    await m.chat.unban_member(target_user.id)
    await m.reply_text(
        strings("unmute_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
    )


@Client.on_message(filters.command("tmute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def tmute(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("error_must_specify_time").format(command=m.command[0])
        )
    split_time = m.text.split(None, 1)
    mute_time = await time_extract(m, split_time[1])
    if not mute_time:
        return
    await c.restrict_chat_member(
        m.chat.id,
        m.reply_to_message.from_user.id,
        ChatPermissions(can_send_messages=False),
        until_date=mute_time,
    )
    await m.reply_text(
        strings("tmute_success").format(
            user=m.reply_to_message.from_user.mention,
            admin=m.from_user.mention,
            time=split_time[1],
        )
    )


@Client.on_message(filters.command("tban", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def tban(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(
            strings("error_must_specify_time").format(command=m.command[0])
        )
    split_time = m.text.split(None, 1)
    ban_time = await time_extract(m, split_time[1])
    if not ban_time:
        return
    await c.kick_chat_member(
        m.chat.id, m.reply_to_message.from_user.id, until_date=ban_time
    )

    await m.reply_text(
        strings("tban_success").format(
            user=m.reply_to_message.from_user.mention,
            admin=m.from_user.mention,
            time=split_time[1],
        )
    )


@Client.on_message(filters.command("purge", prefix))
@require_admin(permissions=["can_delete_messages"], allow_in_private=True)
@use_chat_lang()
async def purge(c: Client, m: Message, strings):
    """ purge upto the replied message """
    status_message = await m.reply_text(strings("purge_in_progress"), quote=True)
    await m.delete()
    message_ids = []
    count_del_etion_s = 0
    if m.reply_to_message:
        for a_s_message_id in range(m.reply_to_message.message_id, m.message_id):
            message_ids.append(a_s_message_id)
            if len(message_ids) == 100:
                await c.delete_messages(
                    chat_id=m.chat.id, message_ids=message_ids, revoke=True
                )
                count_del_etion_s += len(message_ids)
                message_ids = []
        if len(message_ids) > 0:
            await c.delete_messages(
                chat_id=m.chat.id, message_ids=message_ids, revoke=True
            )
            count_del_etion_s += len(message_ids)
    await status_message.edit_text(
        strings("purge_success").format(count=count_del_etion_s)
    )
    await asyncio.sleep(5)
    await status_message.delete()


@Client.on_message(filters.command("antichannelpin", prefix))
@require_admin(permissions=["can_pin_messages"])
async def setantichannelpin(c: Client, m: Message):
    if len(m.text.split()) > 1:
        if m.command[1] == "on":
            toggle_antichannelpin(m.chat.id, True)
            await m.reply_text("anti channel pin for this chat is now enabled.")
        elif m.command[1] == "off":
            toggle_antichannelpin(m.chat.id, None)
            await m.reply_text("anti channel pin for this chat is now disabled.")
        else:
            await m.reply_text("Invalid argument. Use <code>/antichannelpin off/on</code>.")
    else:
        check_acp = check_if_antichannelpin(m.chat.id)
        if check_acp == None:
            await m.reply_text("Anti channel pin is currently disabled in this chat.")
        if check_acp == True:
            await m.reply_text("Anti channel pin is currently enabled in this chat.")


@Client.on_message(filters.linked_channel, group=-1)
async def acp_action(c: Client, m: Message):
    get_acp = check_if_antichannelpin(m.chat.id)
    if get_acp == True:
        await m.unpin()
    else:
        pass


commands.add_command("ban", "admin")
commands.add_command("kick", "admin")
commands.add_command("mute", "admin")
commands.add_command("pin", "admin")
commands.add_command("purge", "admin")
commands.add_command("tban", "admin")
commands.add_command("tmute", "admin")
commands.add_command("unban", "admin")
commands.add_command("unmute", "admin")
commands.add_command("unpin", "admin")
commands.add_command("unpinall", "admin")
