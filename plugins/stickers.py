import os
from urllib.request import urlretrieve

from config import log_chat, prefix
from localization import use_chat_lang
from PIL import Image
from pyrogram import Client, emoji, filters
from pyrogram.errors import PeerIdInvalid, StickersetInvalid
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet
from pyrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
    document,
    input_peer_user,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from utils import EMOJI_PATTERN


@Client.on_message(filters.command(["kang", "kibe", "steal"], prefix))
@use_chat_lang()
async def kang_sticker(c: Client, m: Message, strings):
    prog_msg = await m.reply_text("<code>Kanging sticker ...</code>")
    bot_username = (await c.get_me()).username
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
                return await prog_msg.edit_text(
                    "<b>ERROR</b>: <code>This sticker doesn't a have filename !</code>"
                )
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            if not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit_text("<b>ERROR:</b> <code>Media Invalid<code>")
        pack_prefix = "anim" if animated else "a"
        packname = f"{pack_prefix}_{m.from_user.id}_by_{bot_username}"

        if len(m.command) > 1:
            if m.command[1].isdigit():
                # provide pack number to kang in desired pack
                packname = f"{pack_prefix}{m.command.pop(1)}_{m.from_user.id}_by_{bot_username}"
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
            print("#Sticker - Kang - Failed to Download media.")
            return
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
            print("#Sticker - Kang - no media or image url found.")
            return
        urlretrieve(img_url, filename)
        if len(m.command) > 2:
            # m.command[1] is image_url
            if m.command[2].isdigit():
                packname = f"a{m.command.pop(2)}_{m.from_user.id}_by_{bot_username}"
            if len(m.command) > 2:
                sticker_emoji = (
                    "".join(set(EMOJI_PATTERN.findall("".join(m.command[2:]))))
                    or sticker_emoji
                )
            resize = True
    if resize:
        filename = resize_image(filename)
    max_stickers = 50 if animated else 120
    while not packname_found:
        try:
            stickerset = await c.send(
                GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname))
            )
            if stickerset.set.count >= max_stickers:
                packnum += 1
                packname = f"{pack_prefix}_{packnum}_{m.from_user.id}_by_{bot_username}"
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
            message=f"#Sticker_Kang by User ID -> {m.from_user.id}",
            random_id=c.rnd_id(),
        )
    )
    stkr_file = media.updates[-1].message.media.document
    if packname_found:
        await prog_msg.edit_text("<code>Using existing sticker pack ...</code>")
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
        await prog_msg.edit_text("✨ Creating a new stickerpack")
        try:
            await create_new_pack(c, stkr_file, user, packname, sticker_emoji, animated)
        except PeerIdInvalid:
            return await prog_msg.edit_text(
                "😬 Oops, Looks like I don't have enough permissions to create sticker pack for you !"
                "\n<b>Please start the bot first</b>",
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
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("View", url=f"t.me/addstickers/{packname}")]]
    )
    kanged_success_msg = "Sticker <b>successfully</b> added to pack\nEmoji: {}"
    await prog_msg.edit_text(
        kanged_success_msg.format(sticker_emoji), reply_markup=markup
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


async def create_new_pack(
    c: Client,
    stkr_file: document.Document,
    user: input_peer_user.InputPeerUser,
    packname: str,
    sticker_emoji: str,
    animated: bool,
) -> None:
    await c.send(
        CreateStickerSet(
            user_id=user,
            title=packname,
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
