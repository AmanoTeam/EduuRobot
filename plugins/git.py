from urllib.parse import quote_plus

from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from consts import http
from utils import commands


@Client.on_message(filters.command("git", prefix))
async def git(c: Client, m: Message):
    if len(m.command) == 1:
        return await m.reply_text(
            "Specify a username", reply_to_message_id=m.message_id
        )
    text = m.text.split(maxsplit=1)[1]
    req = await http.get(f"https://api.github.com/users/{text}")
    res = req.json()

    if not res.get("login"):
        return await m.reply_text("User not found", reply_to_message_id=m.message_id)

    avatar = res["avatar_url"]

    anticache = quote_plus((await http.head(avatar)).headers["Last-Modified"])

    caption_text = """<b>Name</b> : <code>{name}</code>
<b>Username</b> : <code>{username}</code>
<b>Location</b> : <code>{location}</code>
<b>Type</b> : <code>{type}</code>
<b>Bio</b> : <code>{bio}</code>
    """
    await m.reply_photo(
        avatar + anticache,
        caption=caption_text.format(
            name=res["name"],
            username=res["login"],
            location=res["location"],
            type=res["type"],
            bio=res["bio"],
        ),
        reply_to_message_id=m.message_id,
    )


commands.add_command("git", "tools")
