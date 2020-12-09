from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from localization import langdict, set_db_lang, use_chat_lang


def gen_langs_kb():
    langs = list(langdict)
    kb = []
    while langs:
        lang = langdict[langs[0]]["main"]
        a = [InlineKeyboardButton(f"{lang['language_flag']} {lang['language_name']}",
                                  callback_data="set_lang "+langs[0])]
        langs.pop(0)
        if langs:
            lang = langdict[langs[0]]["main"]
            a.append(InlineKeyboardButton(f"{lang['language_flag']} {lang['language_name']}",
                                          callback_data="set_lang "+langs[0]))
            langs.pop(0)
        kb.append(a)
    return kb


@Client.on_callback_query(filters.regex("^chlang$"))
@use_chat_lang
async def chlang(c: Client, m: CallbackQuery, strings):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *gen_langs_kb(),
        [InlineKeyboardButton(strings("back_btn", context="general"), callback_data="start_back")]
    ])
    await m.message.edit_text("Here you can change the language used for the bot.", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^set_lang "))
@use_chat_lang
async def set_user_lang(c: Client, m: CallbackQuery, strings):
    set_db_lang(m.message.chat.id, m.message.chat.type, m.data.split()[1])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(strings("back_btn", context="general"), callback_data="start_back")]
    ])
    await m.message.edit_text("Language changed.", reply_markup=keyboard)
