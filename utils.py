import httpx

from pyrogram import Client
from pyrogram.types import Message
from typing import Union
from functools import wraps, partial
from consts import group_types
from localization import get_lang, get_locale_string, default_language, langdict

from dbh import dbc, db


def add_chat(chat_id, chat_type):
    if chat_type == "private":
        dbc.execute("INSERT INTO users (user_id) values (?)", (chat_id,))
        db.commit()
    elif chat_type in group_types: # groups and supergroups share the same table
        dbc.execute("INSERT INTO groups (chat_id,welcome_enabled) values (?,?)", (chat_id, True))
        db.commit()
    elif chat_type == "channel":
        dbc.execute("INSERT INTO channels (chat_id) values (?)", (chat_id,))
        db.commit()
    else:
        raise TypeError("Unknown chat type '%s'." % chat_type)
    return True


def chat_exists(chat_id, chat_type):
    if chat_type == "private":
        dbc.execute("SELECT user_id FROM users where user_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    if chat_type in group_types: # groups and supergroups share the same table
        dbc.execute("SELECT chat_id FROM groups where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    if chat_type == "channel":
        dbc.execute("SELECT chat_id FROM channels where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    raise TypeError("Unknown chat type '%s'." % chat_type)


async def check_perms(client: Client,
                      message: Message,
                      permissions: Union[list, str],
                      complain_missing_perms: bool,
                      strings):
    # TODO: Cache all admin permissions in db.
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator":
        return True

    missing_perms = []

    # No permissions specified, accept being an admin.
    if not permissions and user.status == "administrator":
        return True
    elif user.status != "administrator":
        if complain_missing_perms:
            await message.reply_text(strings("no_admin_error"))
        return False

    if isinstance(permissions, str):
        permissions = [permissions]

    for permission in permissions:
        if not user.__getattribute__(permission):
            missing_perms.append(permission)

    if not missing_perms:
        return True
    elif complain_missing_perms:
        await message.reply_text(strings("no_permission_error").format(permissions=", ".join(missing_perms)))
    return False


def require_admin(permissions: Union[list, str] = None,
                  allow_in_private: bool = False,
                  complain_missing_perms: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message, *args, **kwargs):
            lang = get_lang(message)
            strings = partial(get_locale_string,
                              langdict[lang].get("admin", langdict[default_language]["admin"]),
                              lang, "admin")

            # We don't actually check private and channel chats.
            if message.chat.type == "private":
                if allow_in_private:
                    return await func(client, message, *args, *kwargs)
                else:
                    return await message.reply_text(strings("private_not_allowed"))
            elif message.chat.type == "channel":
                return await func(client, message, *args, *kwargs)
            else:
                has_perms = await check_perms(client, message, permissions, complain_missing_perms, strings)
                if has_perms:
                    return await func(client, message, *args, *kwargs)

        return wrapper
    return decorator
