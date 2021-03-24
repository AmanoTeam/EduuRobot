from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix, log_chat
from localization import use_chat_lang
from utils import commands
from consts import http
from urllib.parse import quote, unquote
from pyrogram.errors.exceptions.bad_request_400 import BadRequest


@Client.on_message(filters.command("mark", prefix))
@use_chat_lang()
async def mark(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("mark_usage"))
    await m.reply(m.text.split(None, 1)[1], parse_mode="markdown")


@Client.on_message(filters.command("html", prefix))
@use_chat_lang()
async def html(c: Client, m: Message, strings):
    if len(m.command) == 1:
        return await m.reply_text(strings("html_usage"))
    await m.reply(m.text.split(None, 1)[1], parse_mode="html")


@Client.on_message(filters.command("admins", prefix) & filters.group)
@use_chat_lang()
async def mentionadmins(c: Client, m: Message, strings):
    mention = ""
    async for i in c.iter_chat_members(m.chat.id, filter="administrators"):
        mention += f"{i.user.mention}\n"
    await c.send_message(m.chat.id, strings("admins_list").format(chat_title=m.chat.title, admins_list=mention))


@Client.on_message(filters.command("token"))
async def getbotinfo(c: Client, m: Message):
    if len(m.command) == 1:
        return await m.reply_text(
            "Specify a bot token", reply_to_message_id=m.message_id
        )
    text = m.text.split(maxsplit=1)[1]
    req = await http.get(f"https://api.telegram.org/bot{text}/getme")
    fullres = req.json()
    if fullres["ok"] == False:
        await m.reply("Invalid bot token")
    elif fullres["ok"] == True:
        res = fullres["result"]
        get_bot_info_text = """<b>Name</b> : <code>{botname}</code>
<b>Username</b> : <code>{botusername}</code>
<b>ID</b> : <code>{botid}</code>
    """
    await m.reply(
        get_bot_info_text.format(
            botname=res["first_name"], botusername=res["username"], botid=res["id"]
        ),
        reply_to_message_id=m.message_id,
    )


@Client.on_message(filters.reply & filters.group & filters.regex(r"(?i)^rt$"))
async def rtcommand(c: Client, m: Message):
    await m.reply(f"🔃 <b>{m.from_user.first_name}</b> retweeted: \n\n 👤 <b>{m.reply_to_message.from_user.first_name}</b>: <i>{m.reply_to_message.text}</i>")


@Client.on_message(filters.command("urlencode", prefix))
async def urlencodecmd(c: Client, m: Message):
    await m.reply_text(quote(m.text.split(None, 1)[1]))


@Client.on_message(filters.command("urldecode", prefix))
async def urldecodecmd(c: Client, m: Message):
    await m.reply_text(unquote(m.text.split(None, 1)[1]))


@Client.on_message(filters.command("bug", prefix))
async def bug_report_cmd(c: Client, m: Message):
    if len(m.text.split()) > 1:
        try:
            await c.send_message(log_chat, f"<b>bug report</b> \n\n from the user {m.from_user.mention} \n ID <code>{m.from_user.id}</code> \n the content of the report: \n <code>{m.text.split(None, 1)[1]}</code>")
        except BadRequest:
            await m.reply_text("error, i cant send the bug report to the admins of the bot")
    else:
        await m.reply("You must specify the bug to report, E.g.: <code>/bug (here the bug)</code>.")


commands.add_command("mark", "general")
commands.add_command("html", "general")
commands.add_command("admins", "general")
commands.add_command("token", "general")
commands.add_command("urlencode", "general")
commands.add_command("urldecode", "general")
