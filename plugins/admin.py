from pyrogram import Client, filters
from config import prefix
from pyrogram.types import ChatPermissions


@Client.on_message(filters.command("pin", prefix))
async def pin(client, message):
    await client.pin_chat_message(
    message.reply_to_message.message_id,
    message.chat.id
    )
    
    
@Client.on_message(filters.command("unpin", prefix))
async def unpin(client, message):
    await client.unpin_chat_message(
    message.reply_to_message.message_id,
    message.chat.id
    )
    
    
@Client.on_message(filters.command("unpinall", prefix))
async def unpinall(client, message):
    await client.unpin_all_chat_messages
    
       
@Client.on_message(filters.command("ban", prefix))
async def ban(client, message):
    await message.chat.kick_member(
    user_id=user_id
    )

    
@Client.on_message(filters.command("kick", prefix))
async def kick(client, message):
    await message.client.kick_chat_member(chat_id, user_id, int(time.time() + 60))
    )
    
@Client.on_message(filters.command("unban", prefix))
async def unban(client, message):
    await message.chat.unban_member(
    user_id=user_id
    )
    
@Client.on_message(filters.command("mute", prefix))
async def mute(client, message):
    await client.restrict_chat_member(message.chat.id,
    message.from_user.id,
    ChatPermissions(can_send_messages=False),
    )
  
    
@Client.on_message(filters.command("unmute", prefix))
async def unmute(client, message):
    await message.chat.unban_member(
    user_id=user_id
    )        
           
