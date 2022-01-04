from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from eduu.config import prefix
from eduu.utils import (
    commands,
    get_reason_text,
    get_target_user,
    require_admin,
    time_extract,
)
from eduu.utils.consts import admin_status
from eduu.utils.localization import use_chat_lang


@Client.on_message(filters.command("mute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def mute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = await get_reason_text(c, m)
    check_admin = await m.chat.get_member(target_user.id)
    if check_admin.status not in admin_status:
        await m.chat.restrict_member(
            target_user.id, ChatPermissions(can_send_messages=False)
        )
        text = strings("mute_success").format(
            user=target_user.mention,
            admin=m.from_user.mention,
        )
        if reason:
            await m.reply_text(
                text + "\n" + strings("reason_string").format(reason_text=reason)
            )
        else:
            await m.reply_text(text)
    else:
        await m.reply_text(strings("i_cant_mute_admins"))


@Client.on_message(filters.command("unmute", prefix))
@use_chat_lang()
@require_admin(permissions=["can_restrict_members"])
async def unmute(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reason = await get_reason_text(c, m)
    await m.chat.unban_member(target_user.id)
    text = strings("unmute_success").format(
        user=target_user.mention,
        admin=m.from_user.mention,
    )
    if reason:
        await m.reply_text(
            text + "\n" + strings("reason_string").format(reason_text=reason)
        )
    else:
        await m.reply_text(text)


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
    await m.chat.restrict_member(
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


commands.add_command("mute", "admin")
commands.add_command("tmute", "admin")
commands.add_command("unmute", "admin")
