from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from localization import use_chat_lang
from utils import commands
from consts import http


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
async def mentionadmins(c: Client, m: Message):
    mention = ""
    async for i in c.iter_chat_members(m.chat.id, filter="administrators"):
        mention += f"{i.user.mention}\n"
    await c.send_message(m.chat.id, f"Admins in the chat {m.chat.title}: \n{mention}")


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


commands.add_command("mark", "general")
commands.add_command("html", "general")
commands.add_command("admins", "general")
commands.add_command("token", "general")
