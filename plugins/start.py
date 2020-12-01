from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from typing import Union

from config import prefix, version
from localization import GetLang


@Client.on_message(filters.command("start", prefix))
@Client.on_callback_query(filters.regex("^start_back$"))
async def start(c: Client, m: Union[Message, CallbackQuery]):
    _ = GetLang(m).strs
    send = m.edit_text if isinstance(m, CallbackQuery) else m.reply_text
    if m.chat.type == "private":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("start.commands_btn"), callback_data="commands")] +
            [InlineKeyboardButton(_("start.infos_btn"), callback_data="infos")],
            [InlineKeyboardButton(_("start.language_btn"), callback_data="chlang")] +
            [InlineKeyboardButton(_("start.add_chat_btn"), url=f"https://t.me/{c.me.username}?startgroup=new")],
        ])
        await send(_("start.private"),
                   reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("start.start_chat"), url=f"https://t.me/{c.me.username}?start=start")]
        ])
        await send(_("start.group"),
                   reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^commands$"))
async def commands(c: Client, m: CallbackQuery):
    _ = GetLang(m).strs
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await m.message.edit_text("commands", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^infos$"))
async def infos(c: Client, m: CallbackQuery):
    _ = GetLang(m).strs
    res = _("start.info_page").format(
        version=version
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await m.message.edit_text(res, reply_markup=keyboard, disable_web_page_preview=True)
