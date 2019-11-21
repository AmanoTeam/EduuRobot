from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from config import prefix, version
from localization import GetLang


@Client.on_message(Filters.command("start", prefix))
async def start(client, message):
    _ = GetLang(message).strs
    if message.chat.type == "private":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("start.commands_btn"), callback_data="commands")] +
            [InlineKeyboardButton(_("start.infos_btn"), callback_data="infos")],
            [InlineKeyboardButton(_("start.language_btn"), callback_data="chlang")] +
            [InlineKeyboardButton(_("➕start.add_chat_btn"), url="https://t.me/{}?startgroup=new")],
        ])
        await message.reply_text(_("start.private"),
                                 reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("start.start_chat"), url="https://t.me/{}?start=start")]
        ])
        await message.reply_text(_("start.group"),
                                 reply_markup=keyboard)


@Client.on_callback_query(Filters.callback_data("commands"))
async def commands(client, message):
    await message.message.edit("commands")


@Client.on_callback_query(Filters.callback_data("infos"))
async def infos(client, message):
    _ = GetLang(message).strs
    res = _("start.info_page").format(
                version=version
            )
    await message.message.edit(res, disable_web_page_preview=True)


@Client.on_callback_query(Filters.callback_data("chlang"))
async def chlang(client, message):
    await message.message.edit("chlang")
