import os, re, youtube_dl

from consts import http

from pyrogram import Client, filters
from pyrogram.types import Message
from config import prefix
from localization import use_chat_lang
from utils import pretty_size


ydl = youtube_dl.YoutubeDL(
    {"outtmpl": "dls/%(title)s.%(ext)s", "format": "140", "noplaylist": True}
)

yt_headers = {"x-youtube-client-name": "1", "x-youtube-client-version": "2.20200827"}


async def search_yt(query):
    url_base = "https://www.youtube.com/results"
    url_yt = "https://www.youtube.com/watch?v="
    r = await http.get(
        url_base, params=dict(search_query=query, pbj="1"), headers=yt_headers
    )
    page = await r.json()
    list_videos = []
    for video in page[1]["response"]["contents"]["twoColumnSearchResultsRenderer"][
        "primaryContents"
    ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]:
        if video.get("videoRenderer"):
            vid_id = video["videoRenderer"]["videoId"]
            title = video["videoRenderer"]["title"]["runs"][0]["text"]
            dic = {"title": title, "url": url_yt + vid_id}
            list_videos.append(dic)
    return list_videos


@Client.on_message(filters.command("yt", prefix))
@use_chat_lang()
async def ytsearchcmd(c: Client, m: Message, strings):
    res = await search_yt(m.text.split(None, 1)[1])
    vids = [
        "{}: <a href='{}'>{}</a>".format(num + 1, i["url"], i["title"])
        for num, i in enumerate(res)
    ]
    await m.reply_text(
        "\n".join(vids) if vids else strings("noresfound"),
        disable_web_page_preview=True,
        parse_mode="html",
    )


@Client.on_message(filters.command("ytdl", prefix))
@use_chat_lang()
async def ytdlcmd(c: Client, m: Message, strings):
    cmdargs = m.text.split(None, 1)[1]
    if cmdargs:
        sentmsg = await m.reply_text(strings("ytdlgetvidinfo"))
        try:
            yt = (
                ydl.extract_info(cmdargs, download=False)
                if re.match(
                    r"^(https?://)?(youtu\.be/|(m\.|www\.)?youtube\.com/watch\?v=).+",
                    cmdargs,
                )
                else ydl.extract_info("ytsearch:" + cmdargs, download=False)["entries"][
                    0
                ]
            )
            for f in yt["formats"]:
                if f["format_id"] == "140":
                    fsize = f["filesize"] or 0
            name = yt["title"]
        except Exception as e:
            return await sentmsg.edit(strings("ytdlerrmsg").format(errmsg=e))
        if not fsize > 200000000:
            if " - " in name:
                performer, title = name.rsplit(" - ", 1)
            else:
                performer = yt.get("creator") or yt.get("uploader")
                title = name
            await sentmsg.edit(
                strings("ytdldownloadmainmsg").format(
                    dwnldname=name, thedownloadsize=pretty_size(fsize)
                ),
                parse_mode="html",
            )
            ydl.download(["https://www.youtube.com/watch?v=" + yt["id"]])
            await sentmsg.edit(strings("ytdlsendaudiomsg"))
            await m.reply_audio(
                audio=open(ydl.prepare_filename(yt), "rb"),
                duration=yt["duration"],
                performer=performer,
                title=title,
            )
            os.remove(ydl.prepare_filename(yt))
            await sentmsg.delete()
        else:
            await sentmsg.edit(
                strings("ytdlerrfiletoobig").format(
                    downloadsizeformat=pretty_size(fsize)
                )
            )
    else:
        await m.reply_text(strings("ytdlusemsg"), parse_mode="markdown")
