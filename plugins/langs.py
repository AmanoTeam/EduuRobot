from pyrogram import CallbackQuery, Client, Filters
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
async def chlang(c: Client, m: CallbackQuery):
    _ = GetLang(m).strs
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *gen_langs_kb(),
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await m.message.edit_text("Here you can change the language used for the bot.", reply_markup=keyboard)


@Client.on_callback_query(callback_starts("set_lang"))
async def set_user_lang(c: Client, m: CallbackQuery):
    set_lang(m.message.chat.id, m.message.chat.type, m.data.split()[1])
    _ = GetLang(m).strs
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(_("general.back_btn"), callback_data="start_back")]
    ])
    await m.message.edit_text("Language changed.", reply_markup=keyboard)
