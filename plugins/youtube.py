import os
import re

import youtube_dl
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import pretty_size, commands
from config import prefix

ydl = youtube_dl.YoutubeDL(
    {"outtmpl": "dls/%(title)s.%(ext)s", "format": "140", "noplaylist": True}
)


@Client.on_message(filters.command("ytdl", prefix))
async def youtube(c: Client, m: Message):
    text = m.text.split(maxsplit=1)[1]
    if text:
        sent_id = await m.reply_text("Getting video information...")
        try:
            if re.match(
                r"^(https?://)?(youtu\.be/|(m\.|www\.)?youtube\.com/watch\?v=).+",
                text,
            ):
                yt = ydl.extract_info(text, download=False)
            else:
                yt = ydl.extract_info("ytsearch:" + text, download=False)["entries"][0]
            for f in yt["formats"]:
                if f["format_id"] == "140":
                    fsize = f["filesize"] or 0
            name = yt["title"]
        except Exception as e:
            return await sent_id.edit_text("Error:\n\n" + str(e))
        if not fsize > 52428800:
            if " - " in name:
                performer, title = name.rsplit(" - ", 1)
            else:
                performer = yt.get("creator") or yt.get("uploader")
                title = name
            await sent_id.edit_text(
                "Downloading <code>{}</code> from YouTube...\n({})".format(
                    name, pretty_size(fsize)
                )
            )
            ydl.download(["https://www.youtube.com/watch?v=" + yt["id"]])
            await sent_id.edit_text("Sending audio...")
            await c.send_chat_action(chat_id=m.chat.id, action="upload_video")
            await c.send_audio(
                chat_id=m.chat.id,
                audio=open(ydl.prepare_filename(yt), "rb"),
                performer=performer,
                title=title,
                duration=yt["duration"],
            )
            os.remove(ydl.prepare_filename(yt))
            await sent_id.delete()
        else:
            await sent_id.edit_text(
                f"The resulting file ({pretty_size(fsize)}) exceeds my 50MB limit",
            )

    else:
        await m.reply_text("<b>Use:</b> /ytdl URL")

    return True


commands.add_command("ytdl", "tools")
