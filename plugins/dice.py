from pyrogram import Client, Filters

from config import prefix
from localization import GetLang


@Client.on_message(Filters.command(["dice", "dados"], prefix))
async def dice(client, message):
    _ = GetLang(message).strs
    dicen = await client.send_dice(message.chat.id, reply_to_message_id=message.message_id)
    await dicen.reply_text(_("dice.result").format(number=dicen.dice.value), quote=True)
