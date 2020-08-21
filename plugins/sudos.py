import asyncio
import html
import io
import os
import re
import sys
import traceback
from contextlib import redirect_stdout

import speedtest
from pyrogram import Client, Filters, Message

from config import sudoers
from localization import GetLang
from utils import meval

prefix = "!"


@Client.on_message(Filters.command("sudos", prefix) & Filters.user(sudoers))
async def sudos(c: Client, m: Message):
    await m.reply_text("Test")


@Client.on_message(Filters.command("cmd", prefix) & Filters.user(sudoers))
async def run_cmd(c: Client, m: Message):
    _ = GetLang(m).strs
    cmd = m.text.split(maxsplit=1)[1]
    if re.match('(?i)poweroff|halt|shutdown|reboot', cmd):
        res = _('sudos.forbidden_command')
    else:
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        res = ("<b>Output:</b>\n<code>{}</code>".format(html.escape(stdout.decode().strip())) if stdout else '') + \
              ("\n<b>Errors:</b>\n<code>{}</code>".format(html.escape(stderr.decode().strip())) if stderr else '')
    await m.reply_text(res)


@Client.on_message(Filters.command("upgrade", prefix) & Filters.user(sudoers))
async def upgrade(c: Client, m: Message):
    _ = GetLang(m).strs
    sm = await m.reply_text("Upgrading sources...")
    proc = await asyncio.create_subprocess_shell(f"git pull --no-edit",
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.STDOUT)
    stdout = (await proc.communicate())[0]
    if proc.returncode == 0:
        if "Already up to date." in stdout.decode():
            await sm.edit_text("There's nothing to upgrade.")
        else:
            await sm.edit_text(_("sudos.restarting"))
            os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        await sm.edit_text(f"Upgrade failed (process exited with {proc.returncode}):\n{stdout.decode()}")
        proc = await asyncio.create_subprocess_shell("git merge --abort")
        stdout = await proc.communicate()


@Client.on_message(Filters.command("eval", prefix) & Filters.user(sudoers))
async def evals(c: Client, m: Message):
    text = m.text[6:]
    try:
        res = await meval(text, locals())
    except:
        ev = traceback.format_exc()
        await m.reply_text(ev)
        return
    else:
        try:
            await m.reply_text(f"<code>{html.escape(str(res))}</code>")
        except Exception as e:
            await m.reply_text(e)


@Client.on_message(Filters.command("exec", prefix) & Filters.user(sudoers))
async def execs(c: Client, m: Message):
    strio = io.StringIO()
    code = m.text.split(maxsplit=1)[1]
    exec('async def __ex(client, message): ' + ' '.join('\n ' + l for l in code.split('\n')))
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](c, m)
        except:
            return await m.reply_text(html.escape(traceback.format_exc()), parse_mode="HTML")

    if strio.getvalue():
        out = f"<code>{html.escape(strio.getvalue())}</code>"
    else:
        out = "Command executed."
    await m.reply_text(out, parse_mode="HTML")


@Client.on_message(Filters.command("speedtest", prefix) & Filters.user(sudoers))
async def test_speed(c: Client, m: Message):
    _ = GetLang(m).strs
    string = _("sudos.speedtest")
    sent = await m.reply_text(string.format(host="", ping="", download="", upload=""))
    s = speedtest.Speedtest()
    bs = s.get_best_server()
    await sent.edit_text(string.format(host=bs["sponsor"], ping=int(bs["latency"]), download="", upload=""))
    dl = round(s.download() / 1024 / 1024, 2)
    await sent.edit_text(string.format(host=bs["sponsor"], ping=int(bs["latency"]), download=dl, upload=""))
    ul = round(s.upload() / 1024 / 1024, 2)
    await sent.edit_text(string.format(host=bs["sponsor"], ping=int(bs["latency"]), download=dl, upload=ul))


@Client.on_message(Filters.command("restart", prefix) & Filters.user(sudoers))
async def restart(c: Client, m: Message):
    _ = GetLang(m).strs
    await m.reply_text(_("sudos.restarting"))
    os.execl(sys.executable, sys.executable, *sys.argv)
