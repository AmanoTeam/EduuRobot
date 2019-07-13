#coding: utf-8
from config import prefix
from localization import get_lang
from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(Filters.command("start", prefix))
async def start(client, message):
    _ = get_lang(message, __name__)
    if message.chat.type == "private":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("Commands"), callback_data="commands")]+
            [InlineKeyboardButton(_("Info"), callback_data="infos")],
            [InlineKeyboardButton(_("Language"), callback_data="chlang")]+
            [InlineKeyboardButton(_("Add to a chat"), url="https://t.me/{}?startgroup=new")],
        ])
        await message.reply(_("Hello! I'm EduuRobot. To discover more about my functions, click on the buttons below."),
                            reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("🤖 Start a chat"), url="https://t.me/{}?start=start")]
        ])
        await message.reply(_("Hello! I'm EduuRobot. Start a conversation with me to discover my functions."),
                            reply_markup=keyboard)


@Client.on_callback_query(Filters.callback_data("commands"))
async def commands(client, message):
    await message.message.edit("commands")


@Client.on_callback_query(Filters.callback_data("infos"))
async def infos(client, message):
    await message.message.edit("infos")


@Client.on_callback_query(Filters.callback_data("chlang"))
async def chlang(client, message):
    await message.message.edit("chlang")
