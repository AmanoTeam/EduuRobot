from pyrogram import CallbackQuery, Client, Filters, Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import prefix, version
from localization import GetLang


@Client.on_message(Filters.command("start", prefix))
async def start(c: Client, m: Message):
    _ = GetLang(m).strs
    if m.chat.type == "private":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("start.commands_btn"), callback_data="commands")] +
            [InlineKeyboardButton(_("start.infos_btn"), callback_data="infos")],
            [InlineKeyboardButton(_("start.language_btn"), callback_data="chlang")] +
            [InlineKeyboardButton(_("start.add_chat_btn"), url="https://t.me/{}?startgroup=new")],
        ])
        await m.reply_text(_("start.private"),
                           reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(_("start.start_chat"), url="https://t.me/{}?start=start")]
        ])
        await m.reply_text(_("start.group"),
                           reply_markup=keyboard)


@Client.on_callback_query(Filters.callback_data("start_back"))
async def start_back(c: Client, m: CallbackQuery):
    _ = GetLang(m).strs
    # TODO: Create a function to generate translatable keyboards instead of duplicating code fragments
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(_("start.commands_btn"), callback_data="commands")] +
        [InlineKeyboardButton(_("start.infos_btn"), callback_data="infos")],
        [InlineKeyboardButton(_("start.language_btn"), callback_data="chlang")] +
        [InlineKeyboardButton(_("start.add_chat_btn"), url="https://t.me/{}?startgroup=new")],
    ])
    await m.message.edit_text(_("start.private"),
                              reply_markup=keyboard)


@Client.on_callback_query(Filters.callback_data("commands"))
async def commands(c: Client, m: CallbackQuery):
    _ = GetLang(m).strs
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await m.message.edit_text("commands", reply_markup=keyboard)


@Client.on_callback_query(Filters.callback_data("infos"))
async def infos(c: Client, m: CallbackQuery):
    _ = GetLang(m).strs
    res = _("start.info_page").format(
        version=version
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await m.message.edit_text(res, reply_markup=keyboard, disable_web_page_preview=True)
