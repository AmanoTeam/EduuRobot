from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from dbh import dbc, db
from localization import use_chat_lang
from utils import require_admin, commands
from .admin import get_target_user


async def get_warn_reason_text(c: Client, m: Message) -> Message:
    reply = m.reply_to_message
    spilt_text = m.text.split
    if not reply and len(spilt_text()) >= 3:
        warn_reason = spilt_text(None, 2)[2]
    elif reply and len(spilt_text()) >= 2:
        warn_reason = spilt_text(None, 1)[1]
    else:
        warn_reason = None
    return warn_reason


dbc.execute(
    """CREATE TABLE IF NOT EXISTS user_warns (user_id INTEGER,
                                              chat_id INTEGER,
                                              count INTEGER)"""
)

admin_status = ["creator", "administrator"]


def get_warns(chat_id, user_id):
    dbc.execute(
        "SELECT count FROM user_warns WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    return dbc.fetchone()[0]


def add_warns(chat_id, user_id, number):
    dbc.execute(
        "SELECT * FROM user_warns WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
    )
    if dbc.fetchone():
        dbc.execute(
            "UPDATE user_warns SET count = count + ? WHERE chat_id = ? AND user_id = ?",
            (number, chat_id, user_id),
        )
        db.commit()
    else:
        dbc.execute(
            "INSERT INTO user_warns (user_id, chat_id, count) VALUES (?,?,?)",
            (user_id, chat_id, number),
        )
        db.commit()


def reset_warns(chat_id, user_id):
    dbc.execute(
        "DELETE FROM user_warns WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
    )
    db.commit()


def get_warns_limit(chat_id):
    dbc.execute("SELECT warns_limit FROM groups WHERE chat_id = ?", (chat_id,))
    res = dbc.fetchone()[0]
    return 3 if res is None else res


def set_warns_limit(chat_id, warns_limit):
    dbc.execute(
        "UPDATE groups SET warns_limit = ? WHERE chat_id = ?", (warns_limit, chat_id)
    )
    db.commit()


@Client.on_message(filters.command("warn", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def warn_user(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    warns_limit = get_warns_limit(m.chat.id)
    check_admin = await c.get_chat_member(m.chat.id, target_user.id)
    reason = await get_warn_reason_text(c, m)
    if check_admin.status not in admin_status:
        add_warns(m.chat.id, target_user.id, 1)
        user_warns = get_warns(m.chat.id, target_user.id)
        if user_warns >= warns_limit:
            await c.kick_chat_member(m.chat.id, target_user.id)
            warn_text = strings("warn_banned").format(
                target_user=target_user.mention, warn_count=user_warns
            )
            reset_warns(m.chat.id, target_user.id)
        else:
            warn_text = strings("user_warned").format(
                target_user=target_user.mention,
                warn_count=user_warns,
                warn_limit=warns_limit,
            )
        if reason:
            await m.reply_text(
                warn_text
                + "\n"
                + strings("warn_reason_text").format(reason_text=reason)
            )
        else:
            await m.reply_text(warn_text)
    else:
        await m.reply_text(strings("warn_cant_admin"))


@Client.on_message(filters.command("setwarnslimit", prefix) & filters.group)
@require_admin(permissions=["can_restrict_members", "can_change_info"])
@use_chat_lang()
async def warns_limit(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("warn_limit_help"))
    try:
        warns_limit = int(m.command[1])
    except ValueError:
        await m.reply_text(strings("warn_limit_invalid"))
    else:
        set_warns_limit(m.chat.id, warns_limit)
        await m.reply(strings("warn_limit_changed").format(warn_limit=warns_limit))


@Client.on_message(filters.command(["resetwarns", "unwarn"], prefix) & filters.group)
@require_admin(permissions=["can_restrict_members"])
@use_chat_lang()
async def unwarn_user(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    reset_warns(m.chat.id, target_user.id)
    await m.reply_text(strings("warn_reset").format(target_user=target_user.mention))


@Client.on_message(filters.command("warns", prefix) & filters.group)
@require_admin()
@use_chat_lang()
async def get_user_warns_cmd(c: Client, m: Message, strings):
    target_user = await get_target_user(c, m)
    user_warns = get_warns(m.chat.id, target_user.id)
    await m.reply_text(
        strings("warns_count_string").format(
            target_user=target_user.mention, warns_count=user_warns
        )
    )


commands.add_command("warn", "admin")
commands.add_command("setwarnslimit", "admin")
commands.add_command("resetwarns", "admin")
commands.add_command("warns", "admin")
