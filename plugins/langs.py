from pyrogram import Client, Filters
from localization import GetLang
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup
from localization import langdict, set_lang


def callback_starts(data: str or bytes):
    return Filters.create(lambda flt, cb: cb.data.split()[0] == flt.data, "CallbackStartsFilter", data=data)


def gen_langs_kb():
    langs = [lang for lang in langdict]
    kb = []
    while langs:
        lang = langdict[langs[0]]
        a = [InlineKeyboardButton(f"{lang['language_flag']} {lang['language_name']}",
                                  callback_data="set_lang "+langs[0])]
        langs.pop(0)
        if langs:
            lang = langdict[langs[0]]
            a.append(InlineKeyboardButton(f"{lang['language_flag']} {lang['language_name']}",
                                          callback_data="set_lang "+langs[0]))
            langs.pop(0)
        kb.append(a)
    return kb


@Client.on_callback_query(Filters.callback_data("chlang"))
async def chlang(client, message):
    _ = GetLang(message).strs
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *gen_langs_kb(),
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await message.message.edit("Here you can change the language used for the bot.", reply_markup=keyboard)


@Client.on_callback_query(callback_starts("set_lang"))
async def set_user_lang(client, message):
    set_lang(message.message.chat.id, message.message.chat.type, message.data.split()[1])
    _ = GetLang(message).strs
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await message.message.edit("Language changed.", reply_markup=keyboard)
