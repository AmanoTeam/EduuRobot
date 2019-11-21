from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton

from config import prefix, version
from localization import GetLang


@Client.on_message(Filters.command("start", prefix))
async def start(client, message):
    _ = GetLang(message).strs
    if message.chat.type == "private":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("📚 Commands"), callback_data="commands")] +
            [InlineKeyboardButton(_("ℹ️ Infos"), callback_data="infos")],
            [InlineKeyboardButton(_("🌎 Language"), callback_data="chlang")] +
            [InlineKeyboardButton(_("➕ Add to a chat"), url="https://t.me/{}?startgroup=new")],
        ])
        await message.reply_text(
            _("Hello! I'm EduuRobot. To discover more about my functions, click on the buttons below."),
            reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("🤖 Start a chat"), url="https://t.me/{}?start=start")]
        ])
        await message.reply_text(_("Hello! I'm EduuRobot. To discover my functions start a conversation with me."),
                                 reply_markup=keyboard)


@Client.on_callback_query(Filters.callback_data("commands"))
async def commands(client, message):
    await message.message.edit("commands")


@Client.on_callback_query(Filters.callback_data("infos"))
async def infos(client, message):
    _ = GetLang(message).strs
    res = _("• EduuRobot\n\n"
            "Version: {version}\n\n"
            "Source Code: [Here](https://github.com/AmanoTeam/EduuRobot)\n"
            "Developers: [Amano Team](https://github.com/AmanoTeam)\n"
            "Owner: [Edu :3](https://t.me/EduBR029)\n\n"
            "Partnerships:\n"
            " » [HPXList - by usernein](https://t.me/hpxlist)\n\n"
            "©2019 - [AmanoTeam™](https://amanoteam.com)").format(
                version=version
            )
    await message.message.edit(res, disable_web_page_preview=True)


@Client.on_callback_query(Filters.callback_data("chlang"))
async def chlang(client, message):
    await message.message.edit("chlang")
