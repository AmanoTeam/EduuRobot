# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2024 Amano LLC

from io import BytesIO

from emoji_regex import emoji_regex
from hydrogram import Client, filters
from hydrogram.enums import MessageEntityType
from hydrogram.errors import PeerIdInvalid, StickersetInvalid
from hydrogram.raw.functions.messages import GetStickerSet, SendMedia
from hydrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet
from hydrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
)
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from PIL import Image, ImageOps

from config import LOG_CHAT, PREFIXES
from eduu.utils import http
from eduu.utils.localization import Strings, use_chat_lang


@Client.on_message(filters.command(["kang", "kibe", "steal"], PREFIXES))
@use_chat_lang
async def kang_sticker(c: Client, m: Message, s: Strings):
    prog_msg = await m.reply_text(s("kang_kanging_sticker_msg"))
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
            not reply.photo and reply.document and "image" in reply.document.mime_type
        ) or reply.photo:
            resize = True
        elif reply.document and "tgsticker" in reply.document.mime_type:
            animated = True
        elif reply.document:
            pass
        elif reply.sticker:
            if not reply.sticker.file_name:
                await prog_msg.edit_text(s("kang_err_sticker_no_file_name"))
                return
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            if not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            await prog_msg.edit_text(s("kang_invalid_media_string"))
            return
        pack_prefix = "anim" if animated else "a"
        packname = f"{pack_prefix}_{m.from_user.id}_by_{bot_username}"

        if len(m.command) > 1 and m.command[1].isdigit() and int(m.command[1]) > 0:
            # provide pack number to kang in desired pack
            packnum = m.command.pop(1)
            packname = f"{pack_prefix}{packnum}_{m.from_user.id}_by_{bot_username}"
        if len(m.command) > 1:
            # matches all valid emojis in input
            sticker_emoji = (
                "".join(set(emoji_regex.findall("".join(m.command[1:])))) or sticker_emoji
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
                file = BytesIO(r.content)
                file.name = "sticker.png"
        except Exception as r_e:
            await prog_msg.edit_text(f"{r_e.__class__.__name__}: {r_e}")
            return
        if len(m.command) > 2:
            if m.command[2].isdigit() and int(m.command[2]) > 0:
                packnum = m.command.pop(2)
                packname = f"a{packnum}_{m.from_user.id}_by_{bot_username}"
            if len(m.command) > 2:
                sticker_emoji = (
                    "".join(set(emoji_regex.findall("".join(m.command[2:])))) or sticker_emoji
                )
            resize = True
    else:
        await prog_msg.delete()
        return
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
                    packname = f"{pack_prefix}_{packnum}_{m.from_user.id}_by_{bot_username}"
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
            await prog_msg.edit_text(s("kang_use_existing_pack"))
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
            await prog_msg.edit_text(s("kang_create_new_pack_string"))
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
                await prog_msg.edit_text(
                    s("kang_cant_create_sticker_pack_string"),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("/start", url=f"https://t.me/{bot_username}?start")]
                    ]),
                )
                return
    except Exception as all_e:
        await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
    else:
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    s("kang_view_sticker_pack_btn"),
                    url=f"t.me/addstickers/{packname}",
                )
            ]
        ])
        kanged_success_msg = s("kang_sticker_kanged_string")
        await prog_msg.edit_text(
            kanged_success_msg.format(sticker_emoji=sticker_emoji), reply_markup=markup
        )


def resize_image(file: str) -> BytesIO:
    im = Image.open(file)
    im = ImageOps.contain(im, (512, 512), method=Image.ANTIALIAS)
    image = BytesIO()
    image.name = "sticker.png"
    im.save(image, "PNG")
    return image


@Client.on_message(filters.command("stickerid", PREFIXES) & filters.reply)
@use_chat_lang
async def getstickerid(c: Client, m: Message, s: Strings):
    if m.reply_to_message.sticker:
        await m.reply_text(
            s("stickerid_string").format(stickerid=m.reply_to_message.sticker.file_id)
        )


@Client.on_message(filters.command("getsticker", PREFIXES) & filters.reply)
@use_chat_lang
async def getstickeraspng(c: Client, m: Message, s: Strings):
    sticker = m.reply_to_message.sticker
    if not sticker:
        await m.reply_text(s("getsticker_not_sticker"))
        return

    if sticker.is_animated:
        await m.reply_text(s("getsticker_animated_not_supported"))
        return

    sticker_file: BytesIO = await m.reply_to_message.download(
        in_memory=True,
    )
    await m.reply_to_message.reply_document(
        document=sticker_file,
        caption=s("getsticker_sticker_info").format(emoji=sticker.emoji, id=sticker.file_id),
    )
