import asyncio
import html
import io
import os
import re
import sys
import traceback
from contextlib import redirect_stdout

import speedtest
from pyrogram import Client, Filters

from config import sudoers
from localization import GetLang
from utils import meval

prefix = "!"


@Client.on_message(Filters.command("sudos", prefix) & Filters.user(sudoers))
async def sudos(client, message):
    await message.reply_text("Test")


@Client.on_message(Filters.command("cmd", prefix) & Filters.user(sudoers))
async def run_cmd(client, message):
    _ = GetLang(message, __name__)._
    cmd = re.split(r"[\n ]+", message.text, 1)[1]
    if re.match('(?i)poweroff|halt|shutdown|reboot', cmd):
        res = _('Forbidden command.')
    else:
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        res = ("<b>Output:</b>\n<code>{}</code>".format(stdout.decode()) if stdout else '') + (
            "\n<b>Errors:</b>\n<code>{}</code>".format(stderr.decode()) if stderr else '')
    await message.reply_text(res)


@Client.on_message(Filters.command("eval", prefix) & Filters.user(sudoers))
async def evals(client, message):
    text = message.text[6:]
    try:
        res = await meval(text, locals())
    except:
        ev = traceback.format_exc()
        await message.reply_text(ev)
        return
    else:
        try:
            await message.reply_text(res)
        except Exception as e:
            await message.reply_text(e)


@Client.on_message(Filters.command("exec", prefix) & Filters.user(sudoers))
async def execs(client, message):
    strio = io.StringIO()
    code = re.split(r"[\n ]+", message.text, 1)[1]
    exec('async def __ex(client, message): ' + ' '.join('\n ' + l for l in code.split('\n')))
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](client, message)
        except:
            return await message.reply_text(html.escape(traceback.format_exc()), parse_mode="HTML")
    await message.reply_text(strio.getvalue() or "ok")


@Client.on_message(Filters.command("speedtest", prefix) & Filters.user(sudoers))
async def test_speed(client, message):
    _ = GetLang(message, __name__)._
    string = _("**Speedtest**\n\n"
               "**🌐 Host:** `{}`\n\n"
               "**🏓 Ping:** `{} ms`\n"
               "**⬇️ Download:** `{} Mbps`\n"
               "**⬆️ Upload:** `{} Mbps`")
    sent = await message.reply_text(string.format("...", "...", "...", "..."))
    s = speedtest.Speedtest()
    bs = s.get_best_server()
    await sent.edit(string.format(bs["sponsor"], int(bs["latency"]), "...", "..."))
    dl = round(s.download() / 1024 / 1024, 2)
    await sent.edit(string.format(bs["sponsor"], int(bs["latency"]), dl, "..."))
    ul = round(s.upload() / 1024 / 1024, 2)
    await sent.edit(string.format(bs["sponsor"], int(bs["latency"]), dl, ul))


@Client.on_message(Filters.command("restart", prefix) & Filters.user(sudoers))
async def restart(client, message):
    _ = GetLang(message, __name__)._
    await message.reply_text(_("Restarting..."))
    os.execl(sys.executable, sys.executable, *sys.argv)
