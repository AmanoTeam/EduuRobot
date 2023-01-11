# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Amano LLC

import io

from PIL import Image, ImageOps
from pyrogram import Client, filters
from pyrogram.enums import MessageEntityType
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

from config import LOG_CHAT, PREFIXES

from ..utils import EMOJI_PATTERN, http
from ..utils.localization import use_chat_lang


@Client.on_message(filters.command(["kang", "kibe", "steal"], PREFIXES))
@use_chat_lang()
async def kang_sticker(c: Client, m: Message, strings):
    prog_msg = await m.reply_text(strings("kanging_sticker_msg"))
    bot_username = c.me.username
    sticker_emoji = "🤔"
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    reply = m.reply_to_message
    user = await c.resolve_peer(m.from_user.username or m.from_user.id)
    if reply and reply.media:
        if (
            not reply.photo
            and reply.document
            and "image" in reply.document.mime_type
            or reply.photo
        ):
            # mime_type: image/webp
            resize = True
        elif reply.document and "tgsticker" in reply.document.mime_type:
            # mime_type: application/x-tgsticker
            animated = True
        elif reply.document:
            pass
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

        if len(m.command) > 1 and m.command[1].isdigit() and int(m.command[1]) > 0:
            # provide pack number to kang in desired pack
            packnum = m.command.pop(1)
            packname = f"{pack_prefix}{packnum}_{m.from_user.id}_by_{bot_username}"
        if len(m.command) > 1:
            # matches all valid emojis in input
            sticker_emoji = (
                "".join(set(EMOJI_PATTERN.findall("".join(m.command[1:]))))
                or sticker_emoji
            )
        file = await c.download_media(m.reply_to_message, in_memory=True)
        if not file:
            # Failed to download
            await prog_msg.delete()
            return
    elif m.entities and len(m.entities) > 1:
        packname = f"a_{m.from_user.id}_by_{bot_username}"
        pack_prefix = "a"
        img_url = next(
            (
                m.text[y.offset : (y.offset + y.length)]
                for y in m.entities
                if y.type == MessageEntityType.URL
            ),
            None,
        )

        if not img_url:
            await prog_msg.delete()
            return
        try:
            r = await http.get(img_url)
            if r.status_code == 200:
                file = io.BytesIO(r.content)
                file.name = "sticker.png"
        except Exception as r_e:
            return await prog_msg.edit_text(f"{r_e.__class__.__name__}: {r_e}")
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
            file = resize_image(file)
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await c.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
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
        ufile = await c.save_file(file)
        media = await c.invoke(
            SendMedia(
                peer=(await c.resolve_peer(LOG_CHAT)),
                media=InputMediaUploadedDocument(
                    file=ufile,
                    mime_type="image/png",
                    attributes=[DocumentAttributeFilename(file_name="sticker.png")],
                ),
                message=f"#Sticker kang by UserID -> {m.from_user.id}",
                random_id=c.rnd_id(),
            )
        )
        stkr_file = media.updates[-1].message.media.document
        if packname_found:
            await prog_msg.edit_text(strings("use_existing_pack"))
            await c.invoke(
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
            u_name = f"@{u_name}" if u_name else str(m.from_user.id)
            stkr_title = f"{u_name}'s "
            if animated:
                stkr_title += "Anim. "
            stkr_title += "EduuPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                await c.invoke(
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


def resize_image(file: str) -> io.BytesIO:
    im = Image.open(file)
    im = ImageOps.contain(im, (512, 512), method=Image.ANTIALIAS)
    image = io.BytesIO()
    image.name = "sticker.png"
    im.save(image, "PNG")
    return image


@Client.on_message(filters.command("stickerid", PREFIXES) & filters.reply)
@use_chat_lang()
async def getstickerid(c: Client, m: Message, strings):
    if m.reply_to_message.sticker:
        await m.reply_text(
            strings("get_sticker_id_string").format(
                stickerid=m.reply_to_message.sticker.file_id
            )
        )


@Client.on_message(filters.command("getsticker", PREFIXES) & filters.reply)
@use_chat_lang()
async def getstickeraspng(c: Client, m: Message, strings):
    sticker = m.reply_to_message.sticker
    if sticker:
        if sticker.is_animated:
            await m.reply_text(strings("animated_not_supported"))
        else:
            sticker_file = await m.reply_to_message.download(
                in_memory=True,
            )
            await m.reply_to_message.reply_document(
                document=sticker_file,
                caption=strings("sticker_info").format(
                    emoji=sticker.emoji, id=sticker.file_id
                ),
            )
    else:
        await m.reply_text(strings("not_sticker"))
