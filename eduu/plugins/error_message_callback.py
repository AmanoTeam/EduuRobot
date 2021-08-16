from pyrogram import Client, filters
from pyrogram.types import CallbackQuery


@Client.on_callback_query(filters.regex(r"^delete_error_message_callback$"))
async def del_error_msg_callback(c: Client, q: CallbackQuery):
    await q.message.delete()
