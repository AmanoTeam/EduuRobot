import gettext
from config import prefix
from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

_ = gettext.gettext


@Client.on_message(Filters.command("start", prefix))
async def start(client, message):
    if message.chat.type == "private":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Comandos", callback_data="commands")]+
            [InlineKeyboardButton("Informações", callback_data="infos")],
            [InlineKeyboardButton("Idioma", callback_data="chlang")]+
            [InlineKeyboardButton("Add em um grupo", url="https://t.me/{}?startgroup=new")],
        ])
        await message.reply(_("Olá! Eu sou o EduuRobot, para descobrir mais sobre minhas funções navegue pelo teclado abaixo:"),
                            reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("🤖 Iniciar uma conversa", url="https://t.me/{}?start=start")]
        ])
        await message.reply("Olá! Eu sou o EduuRobot, para descobrir mais sobre mim, inicie uma conversa comigo.",
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
