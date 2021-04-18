import logging
import os

from config import log_chat, prefix
from consts import http
from localization import use_chat_lang
from PIL import Image
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, StickersetInvalid
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet
from pyrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from utils import EMOJI_PATTERN


@Client.on_message(filters.command(["kang", "kibe", "steal"], prefix))
@use_chat_lang()
async def kang_sticker(c: Client, m: Message, strings):
    prog_msg = await m.reply_text(strings("kanging_sticker_msg"))
    bot_username = c._bot_username
    sticker_emoji = "🤔"
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    reply = m.reply_to_message
    user = await c.resolve_peer(m.from_user.username or m.from_user.id)
    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                # mime_type: image/webp
                resize = True
            elif "tgsticker" in reply.document.mime_type:
                # mime_type: application/x-tgsticker
                animated = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit_text(strings("err_sticker_no_file_name"))
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            if not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit_text(strings("invalid_media_string"))
        pack_prefix = "anim" if animated else "a"
        packname = f"{pack_prefix}_{m.from_user.id}_by_{bot_username}"

        if len(m.command) > 1:
            if m.command[1].isdigit() and int(m.command[1]) > 0:
                # provide pack number to kang in desired pack
                packnum = m.command.pop(1)
                packname = f"{pack_prefix}{packnum}_{m.from_user.id}_by_{bot_username}"
            if len(m.command) > 1:
                # matches all valid emojis in input
                sticker_emoji = (
                    "".join(set(EMOJI_PATTERN.findall("".join(m.command[1:]))))
                    or sticker_emoji
                )
        filename = await c.download_media(m.reply_to_message)
        if not filename:
            # Failed to download
            await prog_msg.delete()
            return logging.error(f" {__name__} - kang - Failed to Download media.")
    elif m.entities and len(m.entities) > 1:
        packname = f"a_{m.from_user.id}_by_{bot_username}"
        # searching if image_url is given
        img_url = None
        filename = "sticker.png"
        for y in m.entities:
            if y.type == "url":
                img_url = m.text[y.offset : (y.offset + y.length)]
                break
        if not img_url:
            await prog_msg.delete()
            return logging.error(f" {__name__} - kang - no media or image url found.")
        try:
            r = await http.get(img_url)
            if r.status_code == 200:
                with open(filename, mode="wb") as f:
                    f.write(r.read())
        except Exception as r_e:
            return await prog_msg.edit_text(f"{r_e.__class__.__name__} : {r_e}")
        if len(m.command) > 2:
            # m.command[1] is image_url
            if m.command[2].isdigit() and int(m.command[2]) > 0:
                packnum = m.command.pop(2)
                packname = f"a{packnum}_{m.from_user.id}_by_{bot_username}"
            if len(m.command) > 2:
                sticker_emoji = (
                    "".join(set(EMOJI_PATTERN.findall("".join(m.command[2:]))))
                    or sticker_emoji
                )
            resize = True
    else:
        return await prog_msg.delete()
    try:
        if resize:
            filename = resize_image(filename)
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await c.send(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname)
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = (
                        f"{pack_prefix}_{packnum}_{m.from_user.id}_by_{bot_username}"
                    )
                else:
                    packname_found = True
            except StickersetInvalid:
                break
        file = await c.save_file(filename)
        media = await c.send(
            SendMedia(
                peer=(await c.resolve_peer(log_chat)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=c.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {m.from_user.id}",
                random_id=c.rnd_id(),
            )
        )
        stkr_file = media.updates[-1].message.media.document
        if packname_found:
            await prog_msg.edit_text(strings("use_existing_pack"))
            await c.send(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit_text(strings("create_new_pack_string"))
            u_name = m.from_user.username
            if u_name:
                u_name = f"@{u_name}"
            else:
                u_name = str(m.from_user.id)
            stkr_title = f"{u_name}'s "
            if animated:
                stkr_title += "Anim. "
            stkr_title += "EduuPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                await c.send(
                    CreateStickerSet(
                        user_id=user,
                        title=stkr_title,
                        short_name=packname,
                        stickers=[
                            InputStickerSetItem(
                                document=InputDocument(
                                    id=stkr_file.id,
                                    access_hash=stkr_file.access_hash,
                                    file_reference=stkr_file.file_reference,
                                ),
                                emoji=sticker_emoji,
                            )
                        ],
                        animated=animated,
                    )
                )
            except PeerIdInvalid:
                return await prog_msg.edit_text(
                    strings("cant_create_sticker_pack_string"),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "/start", url=f"https://t.me/{bot_username}?start"
                                )
                            ]
                        ]
                    ),
                )
    except Exception as all_e:
        await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
    else:
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        strings("view_sticker_pack_btn"),
                        url=f"t.me/addstickers/{packname}",
                    )
                ]
            ]
        )
        kanged_success_msg = strings("sticker_kanged_string")
        await prog_msg.edit_text(
            kanged_success_msg.format(sticker_emoji=sticker_emoji), reply_markup=markup
        )
        # Cleanup
        try:
            os.remove(filename)
        except OSError:
            pass


def resize_image(filename: str) -> str:
    im = Image.open(filename)
    maxsize = 512
    scale = maxsize / max(im.width, im.height)
    sizenew = (int(im.width * scale), int(im.height * scale))
    im = im.resize(sizenew, Image.NEAREST)
    downpath, f_name = os.path.split(filename)
    # not hardcoding png_image as "sticker.png"
    png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
    im.save(png_image, "PNG")
    if png_image != filename:
        os.remove(filename)
    return png_image


@Client.on_message(filters.command("stickerid", prefix) & filters.reply)
@use_chat_lang()
async def getstickerid(c: Client, m: Message, strings):
    if m.reply_to_message.sticker:
        await m.reply_text(
            strings("get_sticker_id_string").format(
                stickerid=m.reply_to_message.sticker.file_id
            )
        )


@Client.on_message(filters.command("getsticker", prefix) & filters.reply)
@use_chat_lang()
async def getstickeraspng(c: Client, m: Message, strings):
    if m.reply_to_message.sticker:
        if m.reply_to_message.sticker.is_animated:
            await m.reply_text(strings("animated_not_supported"))
        if not m.reply_to_message.sticker.is_animated:
            thesticker = await m.reply_to_message.download(file_name="sticker.png")
            await m.reply_to_message.reply_document(thesticker)
            os.remove(thesticker)
