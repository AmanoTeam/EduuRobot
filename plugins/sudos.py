import io
import os
import re
import sys
from pyrogram import Client, Filters
from contextlib import redirect_stdout
from config import sudoers, super_sudoers

prefix = "!"


@Client.on_message(Filters.command("sudos", prefix) & Filters.user(sudoers))
async def sudos(client, message):
    await message.reply("Test")


@Client.on_message(Filters.command("eval", prefix) & Filters.user(sudoers))
async def evals(client, message):
    code = re.split(r"[\n ]+", message.text, 1)[1]
    isasync = re.search(r'\W*?(await )', code)
    if isasync:
        res = await eval(code[:isasync.start(1)] + code[isasync.end(1):])
    else:
        res = eval()
    await message.reply(res or "ok")


@Client.on_message(Filters.command("exec", prefix) & Filters.user(sudoers))
async def execs(client, message):
    strio = io.StringIO()
    code = re.split(r"[\n ]+", message.text, 1)[1]
    exec('async def __ex(client, message): ' + ' '.join('\n ' + l for l in code.split('\n')))
    with redirect_stdout(strio):
        await locals()["__ex"](client, message)
    await message.reply(strio.getvalue() or "ok")


@Client.on_message(Filters.command("restart", prefix) & Filters.user(sudoers))
async def restart(client, message):
    await message.reply("Reiniciando...")
    os.execl(sys.executable, sys.executable, *sys.argv)
