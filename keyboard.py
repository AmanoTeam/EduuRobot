from telepot.namedtuple import InlineKeyboardMarkup
import config

start = InlineKeyboardMarkup(inline_keyboard=[
    [dict(text='🤖 Iniciar uma conversa', url='https://t.me/{}?start='.format(config.bot_username))]
])

start_pv = InlineKeyboardMarkup(inline_keyboard=[
    [dict(text='📚 Comandos', callback_data='all_cmds')] +
    [dict(text='ℹ️ Informações', callback_data='infos')],
    [dict(text='➕ Add em um grupo', url='https://t.me/{}?startgroup=new'.format(config.bot_username))] +
    [dict(text='⭐ Avaliar', url='https://t.me/storebot?start=' + config.bot_username)]
])

all_cmds = InlineKeyboardMarkup(inline_keyboard=[
    [dict(text='👮 Admins', callback_data='admin_cmds')] +
    [dict(text='\ud83d\udc64 Usuários', callback_data='user_cmds')],
    [dict(text='🔧 Ferramentas', callback_data='tools_cmds')] +
    [dict(text='🔎 Modo inline', switch_inline_query_current_chat='/')],
    [dict(text='⬅️ Voltar', callback_data='start_back')]
])

start_back = InlineKeyboardMarkup(inline_keyboard=[
    [dict(text='⬅️ Voltar', callback_data='start_back')]
])

cmds_back = InlineKeyboardMarkup(inline_keyboard=[
    [dict(text='⬅️ Voltar', callback_data='all_cmds')]
])

del_msg = InlineKeyboardMarkup(inline_keyboard=[
    [dict(text='🗑 Deletar mensagem', callback_data='del_msg')]
])

ia_question = InlineKeyboardMarkup(inline_keyboard=[
    [dict(text='✅ Aceitar', callback_data='ia_yes')] +
    [dict(text='❌ Recusar', callback_data='ia_no')]
])
