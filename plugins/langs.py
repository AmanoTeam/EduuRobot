from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from functools import partial

from localization import langdict, set_db_lang, use_chat_lang, get_locale_string, default_language


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
@use_chat_lang()
async def chlang(c: Client, m: CallbackQuery, strings):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *gen_langs_kb(),
        [InlineKeyboardButton(strings("back_btn", context="general"), callback_data="start_back")]
    ])
    await m.message.edit_text(strings("language_changer_private"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^set_lang "))
@use_chat_lang()
async def set_user_lang(c: Client, m: CallbackQuery, strings):
    lang = m.data.split()[1]
    set_db_lang(m.message.chat.id, m.message.chat.type, lang)

    strings = partial(get_locale_string,
                      langdict[lang].get("langs", langdict[default_language]["langs"]),
                      lang, "langs")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(strings("back_btn", context="general"), callback_data="start_back")]
    ])
    await m.message.edit_text(strings("language_changed_successfully"), reply_markup=keyboard)
