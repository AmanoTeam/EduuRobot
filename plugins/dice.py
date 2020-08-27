from pyrogram import Client, filters
from pyrogram.types import Message

from config import prefix
from localization import GetLang


@Client.on_message(filters.command(["dice", "dados"], prefix))
async def dice(c: Client, m: Message):
    _ = GetLang(m).strs
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.message_id)
    await dicen.reply_text(_("dice.result").format(number=dicen.dice.value), quote=True)
