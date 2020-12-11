from pyrogram import Client, filters
from config import prefix
from pyrogram.types import ChatPermissions
from utils import require_admin
from pyrogram.types import Message as message

@Client.on_message(filters.command("pin", prefix))
@require_admin(permissions=["can_pin_messages"])
async def pin(client, message):
    await client.pin_chat_message(
    message.chat.id,
    message.reply_to_message.message_id
    )
    
    
@Client.on_message(filters.command("unpin", prefix))
@require_admin(permissions=["can_pin_messages"])
async def unpin(client, message):
    await client.unpin_chat_message(
    message.chat.id,
    message.reply_to_message.message_id
    )
    
    
@Client.on_message(filters.command("unpinall", prefix))
@require_admin(permissions=["can_pin_messages"])
async def unpinall(client, message):
    await client.unpin_all_chat_messages(
        message.chat.id
    )
    
       
@Client.on_message(filters.command("ban", prefix))
@require_admin(permissions=["can_restrict_members"])
async def ban(client, message):
    await client.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)

    
@Client.on_message(filters.command("kick", prefix))
@require_admin(permissions=["can_restrict_members"])
async def kick(client, message):
    await client.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.chat.unban_member(message.reply_to_message.from_user.id)
    
@Client.on_message(filters.command("unban", prefix))
@require_admin(permissions=["can_restrict_members"])
async def unban(client, message):
    await message.chat.unban_member(message.reply_to_message.from_user.id
    )
    
@Client.on_message(filters.command("mute", prefix))
@require_admin(permissions=["can_restrict_members"])
async def mute(client, message):
    await client.restrict_chat_member(message.chat.id,
     message.reply_to_message.from_user.id,
     ChatPermissions(can_send_messages=False),
       )
  
    
@Client.on_message(filters.command("unmute", prefix))
@require_admin(permissions=["can_restrict_members"])
async def unmute(client, message):
    await message.chat.unban_member(
    user_id=user_id
    )        
           
