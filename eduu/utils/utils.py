# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from __future__ import annotations

import asyncio
import math
import operator
import re
from datetime import datetime, timedelta
from functools import partial
from string import Formatter

import httpx
from hydrogram import Client, filters
from hydrogram.enums import ChatMemberStatus, MessageEntityType
from hydrogram.types import (
    CallbackQuery,
    ChatPrivileges,
    InlineKeyboardButton,
    Message,
    User,
)

from config import SUDOERS

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")

SMART_OPEN = "“"
SMART_CLOSE = "”"
START_CHAR = ("'", '"', SMART_OPEN)


timeout = httpx.Timeout(40, pool=None)

http = httpx.AsyncClient(http2=True, timeout=timeout)


def run_async(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func(*args, **kwargs))


def pretty_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = math.floor(math.log(size_bytes, 1024))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


async def check_perms(
    message: CallbackQuery | Message,
    permissions: ChatPrivileges | None = None,
    complain_missing_perms: bool = True,
    s=None,
) -> bool:
    if isinstance(message, CallbackQuery):
        sender = partial(message.answer, show_alert=True)
        chat = message.message.chat
    else:
        sender = message.reply_text
        chat = message.chat
    # TODO: Cache all admin permissions in db.
    user = await chat.get_member(message.from_user.id)
    if user.status == ChatMemberStatus.OWNER:
        return True

    # No permissions specified, accept being an admin.
    if not permissions and user.status == ChatMemberStatus.ADMINISTRATOR:
        return True
    if user.status != ChatMemberStatus.ADMINISTRATOR:
        if complain_missing_perms:
            await sender(s("admins_no_admin_error"))
        return False

    missing_perms = [
        perm
        for perm, value in permissions.__dict__.items()
        if value and not getattr(user.privileges, perm)
    ]

    if not missing_perms:
        return True
    if complain_missing_perms:
        await sender(s("admins_no_permission_error").format(permissions=", ".join(missing_perms)))
    return False


sudofilter = filters.user(SUDOERS)


async def extract_time(m: Message, time: str) -> datetime | None:
    if time[-1] not in {"m", "h", "d"}:
        await m.reply_text("Invalid time format. Use 'h'/'m'/'d' ")
        return None

    unit = time[-1]
    num = time[:-1]
    if not num.isdigit():
        await m.reply_text("Invalid Amount specified")
        return None

    if unit == "m":
        return datetime.now() + timedelta(minutes=int(num))
    if unit == "h":
        return datetime.now() + timedelta(hours=int(num))
    if unit == "d":
        return datetime.now() + timedelta(days=int(num))

    return None


def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for char in text:
        if is_escaped:
            res += char
            is_escaped = False
        elif char == "\\":
            is_escaped = True
        else:
            res += char
    return res


def split_quotes(text: str) -> list:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1 :].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))


def button_parser(text_note: str) -> tuple[str, list[InlineKeyboardButton]]:
    """Parse a string and return the parsed string and buttons.

    Parameters
    ----------
    markdown_note: str
        The string to parse

    Returns
    -------
    Tuple[str, List[InlineKeyboardButton]]
        The parsed string and buttons
    """
    note_data = ""
    buttons = []
    if text_note is None:
        return note_data, buttons
    if text_note.startswith(("/", "!")):
        args = text_note.split(None, 2)
        text_note = args[2]
    prev = 0
    for match in BTN_URL_REGEX.finditer(text_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            if bool(match.group(4)) and buttons:
                buttons[-1].append(InlineKeyboardButton(text=match.group(2), url=match.group(3)))
            else:
                buttons.append([InlineKeyboardButton(text=match.group(2), url=match.group(3))])
            note_data += text_note[prev : match.start(1)]
            prev = match.end(1)

        else:
            note_data += text_note[prev:to_check]
            prev = match.start(1) - 1

    note_data += text_note[prev:]

    return note_data, buttons


class BotCommands:
    def __init__(self):
        self.commands = {}

    def add_command(
        self,
        command: str,
        category: str,
        aliases: list | None = None,
    ):
        description_key = f"cmd_{command}_description"

        if self.commands.get(category) is None:
            self.commands[category] = []
        self.commands[category].append({
            "command": command,
            "description_key": description_key,
            "aliases": aliases or [],
        })

    def get_commands_message(self, s, category: str | None = None):
        # TODO: Add pagination support.
        if category is None:
            cmds_list = []
            for subcategory in self.commands:
                cmds_list += self.commands[subcategory]
        else:
            cmds_list = self.commands[category]

        res = (
            s("cmds_list_category_title").format(category=s(f"cmds_category_{category}")) + "\n\n"
        )

        cmds_list.sort(key=operator.itemgetter("command"))

        for cmd in cmds_list:
            res += f"<b>/{cmd['command']}</b> - <i>{s(cmd['description_key'])}</i>\n"

        return res


class InlineBotCommands:
    def __init__(self):
        self.commands = []

    def add_command(
        self,
        command: str,
        aliases: list | None = None,
    ):
        description_key = f"inline_cmd_{command.split(maxsplit=1)[0]}_description"

        self.commands.append({
            "command": command,
            "description_key": description_key,
            "aliases": aliases or [],
        })

    def search_commands(self, query: str | None = None):
        return [
            cmd
            for cmd in sorted(self.commands, key=operator.itemgetter("command"))
            if (
                not query
                or query.lower() in cmd["command"]
                or any(query.lower() in alias for alias in cmd["aliases"])
            )
        ]


commands = BotCommands()
inline_commands = InlineBotCommands()


async def get_target_user(c: Client, m: Message) -> User:
    if m.reply_to_message:
        return m.reply_to_message.from_user
    msg_entities = m.entities[1] if m.text.startswith("/") else m.entities[0]
    return await c.get_users(
        msg_entities.user.id
        if msg_entities.type == MessageEntityType.TEXT_MENTION
        else int(m.command[1])
        if m.command[1].isdecimal()
        else m.command[1]
    )


def get_reason_text(c: Client, m: Message) -> Message:
    reply = m.reply_to_message
    spilt_text = m.text.split

    if not reply and len(spilt_text()) >= 3:
        return spilt_text(None, 2)[2]
    if reply and len(spilt_text()) >= 2:
        return spilt_text(None, 1)[1]

    return None


# Thank github.com/usernein for shell_exec
async def shell_exec(code):
    process = await asyncio.create_subprocess_shell(
        code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )

    stdout = (await process.communicate())[0].decode().strip()
    return stdout, process


def get_format_keys(string: str) -> list[str]:
    """Return a list of formatting keys present in string.

    Parameters
    ----------
    string: str
        The string to parse.

    Returns
    -------
    List[str]
        A list of formatting keys present in string.
    """
    return [i[1] for i in Formatter().parse(string) if i[1] is not None]


def linkify_commit(commit: str) -> str:
    """Return a link to a commit."""
    return f'<a href="https://github.com/AmanoTeam/EduuRobot/commit/{commit}">{commit}</a>'
