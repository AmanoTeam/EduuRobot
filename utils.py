import html
import inspect
import os.path
import time
from functools import wraps, partial
from typing import Union, Tuple, Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from config import sudoers
from consts import group_types
from dbh import dbc, db
from localization import get_lang, get_locale_string, default_language, langdict


def add_chat(chat_id, chat_type):
    if chat_type == "private":
        dbc.execute("INSERT INTO users (user_id) values (?)", (chat_id,))
        db.commit()
    elif chat_type in group_types:  # groups and supergroups share the same table
        dbc.execute(
            "INSERT INTO groups (chat_id,welcome_enabled) values (?,?)", (chat_id, True)
        )
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
    if chat_type in group_types:  # groups and supergroups share the same table
        dbc.execute("SELECT chat_id FROM groups where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    if chat_type == "channel":
        dbc.execute("SELECT chat_id FROM channels where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    raise TypeError("Unknown chat type '%s'." % chat_type)


def del_restarted():
    dbc.execute("DELETE FROM was_restarted_at")
    db.commit()


def get_restarted() -> Tuple[int, int]:
    dbc.execute("SELECT chat_id, message_id FROM was_restarted_at")
    return dbc.fetchone()


def set_restarted(chat_id: int, message_id: int):
    dbc.execute("INSERT INTO was_restarted_at VALUES (?, ?)", (chat_id, message_id))
    db.commit()


async def check_perms(
    client: Client,
    message: Message,
    permissions: Optional[Union[list, str]],
    complain_missing_perms: bool,
    strings,
) -> bool:
    # TODO: Cache all admin permissions in db.
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator":
        return True

    missing_perms = []

    # No permissions specified, accept being an admin.
    if not permissions and user.status == "administrator":
        return True
    if user.status != "administrator":
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
    if complain_missing_perms:
        await message.reply_text(
            strings("no_permission_error").format(permissions=", ".join(missing_perms))
        )
    return False


def require_admin(
    permissions: Union[list, str] = None,
    allow_in_private: bool = False,
    complain_missing_perms: bool = True,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message, *args, **kwargs):
            lang = get_lang(message)
            strings = partial(
                get_locale_string,
                langdict[lang].get("admin", langdict[default_language]["admin"]),
                lang,
                "admin",
            )

            # We don't actually check private and channel chats.
            if message.chat.type == "private":
                if allow_in_private:
                    return await func(client, message, *args, *kwargs)
                return await message.reply_text(strings("private_not_allowed"))
            if message.chat.type == "channel":
                return await func(client, message, *args, *kwargs)
            has_perms = await check_perms(
                client, message, permissions, complain_missing_perms, strings
            )
            if has_perms:
                return await func(client, message, *args, *kwargs)

        return wrapper

    return decorator


sudofilter = filters.user(sudoers)


async def time_extract(m: Message, t: str) -> int:
    if t[-1] in ["m", "h", "d"]:
        print(True)
        unit = t[-1]
        num = t[:-1]
        if not num.isdigit():
            await m.reply_text("Invalid Amount specified")
            return

        if unit == "m":
            t_time = int(num) * 60
        elif unit == "h":
            t_time = int(num) * 60 * 60
        elif unit == "d":
            t_time = int(num) * 24 * 60 * 60
        else:
            return 0
        return int(time.time() + t_time)
    await m.reply_text("Invalid time format. Use 'h'/'m'/'d' ")
    return 0


def html_user(name: str, user_id: int):
    name = html.escape(name)
    _html = f"<a href='tg://user?id={user_id}'>{name}</a>"
    return _html


class BotCommands:
    def __init__(self):
        self.commands = {}

    def add_command(
        self,
        command: str,
        category: str,
        description_key: str = None,
        context_location: str = None,
    ):
        if context_location is None:
            # If context_location is not defined, get context from file name who added the command
            frame = inspect.stack()[1]
            context_location = (
                frame[0].f_code.co_filename.split(os.path.sep)[-1].split(".")[0]
            )
        if description_key is None:
            description_key = command + "_description"
        if self.commands.get(category) is None:
            self.commands[category] = []
        self.commands[category].append(
            dict(
                command=command,
                description_key=description_key,
                context=context_location,
            )
        )

    def get_commands_message(self, strings_manager, category: str = None):
        # TODO: Add pagination support.
        if category is None:
            cmds_list = []
            for category in self.commands:
                cmds_list += self.commands[category]
        else:
            cmds_list = self.commands[category]

        res = (
            strings_manager("command_category_title").format(
                category=strings_manager(category)
            )
            + "\n\n"
        )

        cmds_list.sort(key=lambda k: k["command"])

        for cmd in cmds_list:
            res += f"<b>/{cmd['command']}</b> - <i>{strings_manager(cmd['description_key'], context=cmd['context'])}</i>\n"

        return res


commands = BotCommands()
