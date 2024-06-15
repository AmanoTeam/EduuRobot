# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from __future__ import annotations

import asyncio
import html
import io
import os
import re
import sys
import time
import traceback
from contextlib import redirect_stdout, suppress
from sqlite3 import IntegrityError, OperationalError
from typing import TYPE_CHECKING

import humanfriendly
import speedtest
from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.errors import RPCError
from meval import meval

from config import DATABASE_PATH
from eduu.database import database
from eduu.database.restarted import set_restarted
from eduu.utils import sudofilter
from eduu.utils.localization import use_chat_lang
from eduu.utils.utils import shell_exec

if TYPE_CHECKING:
    from hydrogram.types import Message

prefix: list | str = "!"

conn = database.get_conn()


@Client.on_message(filters.command("sudos", prefix) & sudofilter)
async def sudos(c: Client, m: Message):
    await m.reply_text("Test")


@Client.on_message(filters.command("cmd", prefix) & sudofilter)
@use_chat_lang
async def run_cmd(c: Client, m: Message, s):
    cmd = m.text.split(maxsplit=1)[1]
    if re.match("(?i)poweroff|halt|shutdown|reboot", cmd):
        await m.reply_text(s("sudos_forbidden_command"))
        return

    stdout, stderr = await shell_exec(cmd)
    await m.reply_text(
        (f"<b>Output:</b>\n<code>{html.escape(stdout)}</code>" if stdout else "")
        + (f"\n<b>Errors:</b>\n<code>{stderr}</code>" if stderr else "")
    )


@Client.on_message(filters.command("upgrade", prefix) & sudofilter)
@use_chat_lang
async def upgrade(c: Client, m: Message, s):
    sm = await m.reply_text("Upgrading sources…")
    stdout, proc = await shell_exec("git pull --no-edit")
    if proc.returncode != 0:
        await sm.edit_text(f"Upgrade failed (process exited with {proc.returncode}):\n{stdout}")
        proc = await asyncio.create_subprocess_shell("git merge --abort")
        await proc.communicate()
        return

    if "Already up to date." in stdout:
        await sm.edit_text("There's nothing to upgrade.")
    else:
        await sm.edit_text(s("sudos_restarting"))
        await set_restarted(sm.chat.id, sm.id)
        await conn.commit()
        args = [sys.executable, "-m", "eduu"]
        os.execv(sys.executable, args)  # skipcq: BAN-B606


@Client.on_message(filters.command("eval", prefix) & sudofilter)
async def evals(c: Client, m: Message):
    text = m.text.split(maxsplit=1)[1]
    try:
        res = await meval(text, globals(), **locals())
    except BaseException:  # skipcq
        ev = traceback.format_exc()
        await m.reply_text(f"<code>{html.escape(ev)}</code>")
    else:
        try:
            await m.reply_text(f"<code>{html.escape(str(res))}</code>")
        except BaseException as e:  # skipcq
            await m.reply_text(str(e))


@Client.on_message(filters.command("exec", prefix) & sudofilter)
async def execs(c: Client, m: Message):
    strio = io.StringIO()
    code = m.text.split(maxsplit=1)[1]
    exec(
        "async def __ex(c, m): " + " ".join("\n " + line for line in code.split("\n"))
    )  # skipcq: PYL-W0122
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](c, m)
        except BaseException:  # skipcq
            await m.reply_text(html.escape(traceback.format_exc()))
            return

    if strio.getvalue().strip():
        out = f"<code>{html.escape(strio.getvalue())}</code>"
    else:
        out = "Command executed."
    await m.reply_text(out)


@Client.on_message(filters.command("sudos_speedtest", prefix) & sudofilter)
@use_chat_lang
async def test_speed(c: Client, m: Message, s):
    string = s("sudos_speedtest")
    sent = await m.reply_text(string.format(host="", ping="", download="", upload=""))
    s = speedtest.Speedtest()
    bs = s.get_best_server()
    await sent.edit_text(
        string.format(host=bs["sponsor"], ping=int(bs["latency"]), download="", upload="")
    )
    dl = round(s.download() / 1024 / 1024, 2)
    await sent.edit_text(
        string.format(host=bs["sponsor"], ping=int(bs["latency"]), download=dl, upload="")
    )
    ul = round(s.upload() / 1024 / 1024, 2)
    await sent.edit_text(
        string.format(host=bs["sponsor"], ping=int(bs["latency"]), download=dl, upload=ul)
    )


@Client.on_message(filters.command("sql", prefix) & sudofilter)
async def execsql(c: Client, m: Message):
    command = m.text.split(maxsplit=1)[1]

    try:
        ex = await conn.execute(command)
    except (IntegrityError, OperationalError) as e:
        await m.reply_text(f"SQL executed with an error: {e.__class__.__name__}: {e}")
        return

    ret = await ex.fetchall()
    await conn.commit()

    if not ret:
        await m.reply_text("SQL executed successfully and without any return.")
        return

    res = "|".join([name[0] for name in ex.description]) + "\n"
    res += "\n".join(["|".join(str(s) for s in items) for items in ret])

    if len(res) < 3500:
        await m.reply_text(f"<code>{res}</code>")
        return

    bio = io.BytesIO()
    bio.name = "output.txt"

    bio.write(res.encode())

    await m.reply_document(bio)


@Client.on_message(filters.command("restart", prefix) & sudofilter)
@use_chat_lang
async def restart(c: Client, m: Message, s):
    sent = await m.reply_text(s("sudos_restarting"))
    await set_restarted(sent.chat.id, sent.id)
    await conn.commit()
    args = [sys.executable, "-m", "eduu"]
    os.execv(sys.executable, args)  # skipcq: BAN-B606


@Client.on_message(filters.command("leave", prefix) & sudofilter)
async def leave_chat(c: Client, m: Message):
    if len(m.command) == 1:
        with suppress(RPCError):
            await m.chat.leave()
    else:
        chat_id = m.text.split(maxsplit=1)[1]
        with suppress(RPCError):
            await c.leave_chat(int(chat_id))


@Client.on_message(filters.command(["bot_stats", "stats"], prefix) & sudofilter)
async def getbotstats(c: Client, m: Message):
    users_count = await conn.execute("select count() from users")
    users_count = await users_count.fetchone()
    groups_count = await conn.execute("select count() from groups")
    groups_count = await groups_count.fetchone()
    filters_count = await conn.execute("select count() from filters")
    filters_count = await filters_count.fetchone()
    notes_count = await conn.execute("select count() from notes")
    notes_count = await notes_count.fetchone()
    bot_uptime = round(time.time() - c.start_time)
    bot_uptime = humanfriendly.format_timespan(bot_uptime)

    await m.reply_text(
        "<b>Bot statistics:</b>\n\n"
        f"<b>Users:</b> {users_count[0]}\n"
        f"<b>Groups:</b> {groups_count[0]}\n"
        f"<b>Filters:</b> {filters_count[0]}\n"
        f"<b>Notes:</b> {notes_count[0]}\n\n"
        f"<b>Uptime:</b> {bot_uptime}"
    )


@Client.on_message(filters.command("del", prefix) & sudofilter)
async def del_message(c: Client, m: Message):
    err = ""
    try:
        await c.delete_messages(m.chat.id, m.reply_to_message.id)
    except RPCError as e:
        err += e
    try:
        await c.delete_messages(m.chat.id, m.id)
    except RPCError as e:
        err += e

    await m.reply_text(err)


@Client.on_message(
    filters.command("backup", prefix)
    & sudofilter
    & ~filters.forwarded
    & ~filters.group
    & ~filters.via_bot
)
async def backupcmd(c: Client, m: Message):
    await m.reply_document(DATABASE_PATH)


@Client.on_message(filters.command("upload", prefix) & sudofilter)
async def uploadfile(c: Client, m: Message):
    if not m.reply_to_message:
        await m.reply_text("You must reply to a file to upload.")

    sent = await m.reply_to_message.reply_text("Uploading file…")
    file_path = await m.reply_to_message.download(m.command[1] if len(m.command) > 1 else "")
    await sent.edit_text(f"File successfully saved to {file_path}.")


@Client.on_message(filters.command("doc", prefix) & sudofilter)
async def downloadfile(c: Client, m: Message):
    if len(m.text.split()) > 1:
        await m.reply_document(m.command[1])
    else:
        await m.reply_text("You must specify the document path.")


@Client.on_message(filters.command("chat", prefix) & sudofilter)
async def getchatcmd(c: Client, m: Message):
    if len(m.text.split()) == 1:
        await m.reply_text("You must specify the Chat.")
        return

    targetchat = await c.get_chat(m.command[1])
    if targetchat.type == ChatType.PRIVATE:
        await m.reply_text("This is a private Chat.")
        return

    await m.reply_text(
        f"<b>Title:</b> {targetchat.title}\n<b>Username:</b> {targetchat.username}\n<b>Members:</b> {targetchat.members_count}"
    )
