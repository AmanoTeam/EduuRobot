import io
import os
import re
import sys
import html
import asyncio
import traceback
import speedtest
from localization import GetLang
from pyrogram import Client, Filters
from contextlib import redirect_stdout
from config import sudoers

prefix = "!"


@Client.on_message(Filters.command("sudos", prefix) & Filters.user(sudoers))
async def sudos(client, message):
    await message.reply("Test")


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
        res = ("<b>Output:</b>\n<code>{}</code>".format(stdout.decode())  if stdout else '') + (
               "\n\n<b>Errors:</b>\n<code>{}</code>".format(stderr.decode())  if stderr else '')
    await message.reply(res)


@Client.on_message(Filters.command("eval", prefix) & Filters.user(sudoers))
async def evals(client, message):
    code = re.split(r"[\n ]+", message.text, 1)[1]
    isasync = re.search(r'\W*?(await )', code)
    try:
        res = await eval(code[:isasync.start(1)] + code[isasync.end(1):]) if isasync else eval(code)
    except Exception as e:
        res = str(e)
    await message.reply(html.escape(str(res)), parse_mode="HTML")


@Client.on_message(Filters.command("exec", prefix) & Filters.user(sudoers))
async def execs(client, message):
    strio = io.StringIO()
    code = re.split(r"[\n ]+", message.text, 1)[1]
    exec('async def __ex(client, message): ' + ' '.join('\n ' + l for l in code.split('\n')))
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](client, message)
        except:
            return await message.reply(html.escape(traceback.format_exc()), parse_mode="HTML")
    await message.reply(strio.getvalue() or "ok")


@Client.on_message(Filters.command("speedtest", prefix) & Filters.user(sudoers))
async def test_speed(client, message):
    _ = GetLang(message, __name__)._
    string = _("**Speedtest**\n\n"
               "**🌐 Host:** `{}`\n\n"
               "**🏓 Ping:** `{} ms`\n"
               "**⬇️ Download:** `{} Mbps`\n"
               "**⬆️ Upload:** `{} Mbps`")
    sent = await message.reply(string.format("...", "...", "...", "..."))
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
    await message.reply(_("Restarting..."))
    os.execl(sys.executable, sys.executable, *sys.argv)
