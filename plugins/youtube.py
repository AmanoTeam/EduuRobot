import datetime
import io
import functools
import os
import re
import time
import shutil
import tempfile

import youtube_dl
from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from config import prefix
from consts import http
from localization import use_chat_lang
from utils import aiowrap, pretty_size


@aiowrap
def extract_info(instance, url, download=True):
    return instance.extract_info(url, download)


@Client.on_message(filters.command("ytdl", prefix))
@use_chat_lang()
async def ytdlcmd(c: Client, m: Message, strings):
    user = m.from_user.id

    if m.reply_to_message and m.reply_to_message.text:
        url = m.reply_to_message.text
    elif len(m.command) > 1:
        url = m.text.split(None, 1)[1]
    else:
        await m.reply_text(strings("ytdl_missing_argument"))
        return

    ydl = youtube_dl.YoutubeDL(
        {"outtmpl": "dls/%(title)s-%(id)s.%(ext)s", "format": "mp4", "noplaylist": True}
    )
    rege = re.match(
        r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?",
        url,
        re.M,
    )

    if not rege:
        yt = await extract_info(ydl, "ytsearch:" + url, download=False)
        yt = yt["entries"][0]
    else:
        yt = await extract_info(ydl, rege.group(), download=False)

    for f in yt["formats"]:
        if f["format_id"] == "140":
            afsize = f["filesize"] or 0
        if f["ext"] == "mp4" and f["filesize"] is not None:
            vfsize = f["filesize"] or 0
            vformat = f["format_id"]

    keyboard = [
        [
            (
                strings("ytdl_audio_button"),
                f'_aud.{yt["id"]}|{afsize}|{vformat}|{m.chat.id}|{user}|{m.message_id}',
            ),
            (
                strings("ytdl_video_button"),
                f'_vid.{yt["id"]}|{vfsize}|{vformat}|{m.chat.id}|{user}|{m.message_id}',
            ),
        ]
    ]

    if " - " in yt["title"]:
        performer, title = yt["title"].rsplit(" - ", 1)
    else:
        performer = yt.get("creator") or yt.get("uploader")
        title = yt["title"]

    text = f"🎧 <b>{performer}</b> - <i>{title}</i>\n"
    text += f"💾 <code>{pretty_size(afsize)}</code> (audio) / <code>{pretty_size(int(vfsize))}</code> (video)\n"
    text += f"⏳ <code>{datetime.timedelta(seconds=yt.get('duration'))}</code>"

    await m.reply_text(text, reply_markup=ikb(keyboard))


@Client.on_callback_query(filters.regex("^(_(vid|aud))"))
@use_chat_lang()
async def cli_ytdl(c: Client, cq: CallbackQuery, strings):
    data, fsize, vformat, cid, userid, mid = cq.data.split("|")
    if not cq.from_user.id == int(userid):
        return await cq.answer(
            strings("ytdl_button_denied"), cache_time=60, is_personal=True
        )
    if int(fsize) > 200000000:
        return await cq.answer(
            strings("ytdl_file_too_big"),
            show_alert=True,
            cache_time=60,
        )
    vid = re.sub(r"^\_(vid|aud)\.", "", data)
    url = "https://www.youtube.com/watch?v=" + vid
    await cq.message.edit(strings("ytdl_downloading"))
    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "ytdl")
    last_edit = 0

    def progress(m, d):
        nonlocal last_edit

        if d["status"] == "finished":
            return
        if d["status"] == "downloading":
            if last_edit + 1 < int(time.time()):
                percent = d["_percent_str"]
                try:
                    m.edit(f"{strings('ytdl_downloading')} {percent}")
                except BadRequest:
                    pass
                finally:
                    last_edit = int(time.time())

    if "vid" in data:
        ydl = youtube_dl.YoutubeDL(
            {
                "outtmpl": f"{path}/%(title)s-%(id)s.%(ext)s",
                "format": vformat,
                "noplaylist": True,
            }
        )
    else:
        ydl = youtube_dl.YoutubeDL(
            {
                "outtmpl": f"{path}/%(title)s-%(id)s.%(ext)s",
                "format": "140",
                "extractaudio": True,
                "noplaylist": True,
            }
        )
    ydl.add_progress_hook(functools.partial(progress, cq.message))
    try:
        yt = await extract_info(ydl, url, download=True)
    except BaseException as e:
        await cq.message.edit(strings("ytdl_send_error").format(errmsg=e))
        return
    await cq.message.edit(strings("ytdl_sending"))
    filename = ydl.prepare_filename(yt)
    thumb = io.BytesIO((await http.get(yt["thumbnail"])).content)
    thumb.name = "thumbnail.png"
    if "vid" in data:
        try:
            await c.send_video(
                int(cid),
                filename,
                width=1920,
                height=1080,
                caption=yt["title"],
                duration=yt["duration"],
                thumb=thumb,
                reply_to_message_id=int(mid),
            )
        except BadRequest as e:
            await c.send_message(
                chat_id=int(cid),
                text=strings("ytdl_send_error").format(errmsg=e),
                reply_to_message_id=int(mid),
            )
    else:
        if " - " in yt["title"]:
            performer, title = yt["title"].rsplit(" - ", 1)
        else:
            performer = yt.get("creator") or yt.get("uploader")
            title = yt["title"]
        try:
            await c.send_audio(
                int(cid),
                filename,
                title=title,
                performer=performer,
                duration=yt["duration"],
                thumb=thumb,
                reply_to_message_id=int(mid),
            )
        except BadRequest as e:
            await c.send_message(
                chat_id=int(cid),
                text=strings("ytdl_send_error").format(errmsg=e),
                reply_to_message_id=int(mid),
            )
    await cq.message.delete()

    shutil.rmtree(tempdir, ignore_errors=True)
