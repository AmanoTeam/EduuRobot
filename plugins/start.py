from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from config import prefix, version
from localization import use_chat_lang


@Client.on_message(filters.command("start", prefix))
@Client.on_callback_query(filters.regex("^start_back$"))
@use_chat_lang()
async def start(c: Client, m: Message, strings):
    if m.chat.type == "private":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(strings("commands_btn"), callback_data="commands")] +
            [InlineKeyboardButton(strings("infos_btn"), callback_data="infos")],
            [InlineKeyboardButton(strings("language_btn"), callback_data="chlang")] +
            [InlineKeyboardButton(strings("add_chat_btn"), url=f"https://t.me/{c.me.username}?startgroup=new")],
        ])
        await m.reply_text(strings("private"),
                           reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(strings("start_chat"), url=f"https://t.me/{c.me.username}?start=start")]
        ])
        await m.reply_text(strings("group"),
                           reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^start_back$"))
@use_chat_lang()
async def start_back(c: Client, m: CallbackQuery, strings):
    # TODO: Create a function to generate translatable keyboards instead of duplicating code fragments
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(strings("commands_btn"), callback_data="commands")] +
        [InlineKeyboardButton(strings("infos_btn"), callback_data="infos")],
        [InlineKeyboardButton(strings("language_btn"), callback_data="chlang")] +
        [InlineKeyboardButton(strings("add_chat_btn"), url=f"https://t.me/{c.me.username}?startgroup=new")],
    ])
    await m.message.edit_text(strings("private"),
                              reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^commands$"))
@use_chat_lang()
async def commands(c: Client, m: CallbackQuery, strings):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(strings("back_btn", context="general"), callback_data="start_back")]
    ])
    await m.message.edit_text("commands", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^infos$"))
@use_chat_lang()
async def infos(c: Client, m: CallbackQuery, strings):
    res = strings("info_page").format(
        version=version
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(strings("back_btn", context="general"), callback_data="start_back")]
    ])
    await m.message.edit_text(res, reply_markup=keyboard, disable_web_page_preview=True)
