#coding: utf-8
import speedtest
from pyrogram import Client, Filters
from config import sudoers

string = """**Teste de velocidade**

**🌐 Host:** `{}`

**🏓 Ping:** `{} ms`
**⬇️ Download:** `{} Mbps`
**⬆️ Upload:** `{} Mbps`"""


@Client.on_message(Filters.command("speedtest") & Filters.user(sudoers))
async def test_speed(client, message):
    sent = await message.reply(string.format("...", "...", "...", "..."))
    s = speedtest.Speedtest()
    bs = s.get_best_server()
    await sent.edit(string.format(bs["sponsor"], int(bs["latency"]), "...", "..."))
    dl = round(s.download() / 1024 / 1024, 2)
    await sent.edit(string.format(bs["sponsor"], int(bs["latency"]), dl, "..."))
    ul = round(s.upload() / 1024 / 1024, 2)
    await sent.edit(string.format(bs["sponsor"], int(bs["latency"]), dl, ul))
