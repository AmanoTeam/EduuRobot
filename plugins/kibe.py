# Copyright (C) 2018-2020 Amano Team <contact@amanoteam.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import time
import math

from amanobot.exception import TelegramError
from amanobot.namedtuple import InlineKeyboardMarkup

from config import bot, bot_username
from PIL import Image


async def kibe(msg):
    if msg.get('text'):
        if msg['text'].startswith('/kibe_stickerid') or msg['text'].startswith('!stickerid'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                await bot.sendMessage(msg['chat']['id'], "Sticker ID:\n```" +
                                      msg['reply_to_message']['sticker']['file_id'] + "```",
                                      parse_mode='markdown', reply_to_message_id=msg['message_id'])
            else:
                await bot.sendMessage(msg['chat']['id'], "Please reply to a sticker to get its ID.",
                                      reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/kibe_getsticker') or msg['text'].startswith('!getsticker'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                chat_id = msg['chat']['id']
                file_id = msg['reply_to_message']['sticker']['file_id']
                await bot.download_file(file_id, 'sticker.png')
                await bot.sendDocument(chat_id, document=open('sticker.png', 'rb'))
                os.remove("sticker.png")
            else:
                await bot.sendMessage(msg['chat']['id'], "Please reply to a sticker for me to upload its PNG.",
                                      reply_to_message_id=msg['message_id'])
            return True


        elif msg['text'].startswith('/kibe') or msg['text'].startswith('!kibe'):
            if msg.get('reply_to_message'):
                emoji = msg['text'][5:]
                rmsg = msg['reply_to_message']
                packname = "a" + str(msg['from']['id']) + "_by_" + bot_username
                rsize = False
                anim = False
                if rmsg.get('document'):
                    await bot.download_file(rmsg['document']['file_id'], str(msg['from']['id']) + '_kibe_sticker.png')
                    name = str(msg['from']['id']) + '_kibe_sticker.png'
                    rsize = True
                elif rmsg.get('photo'):
                    await bot.download_file(rmsg['photo'][-1]['file_id'], str(msg['from']['id']) + '_kibe_sticker.png')
                    name = str(msg['from']['id']) + '_kibe_sticker.png'
                    rsize = True
                elif rmsg.get('sticker'):
                    if len(emoji) == 0:
                        emoji = rmsg['sticker']['emoji']
                    if rmsg['sticker']['is_animated']:
                        anim = True
                        await bot.download_file(rmsg['sticker']['file_id'], str(msg['from']['id']) + '_kibe_sticker.tgs')
                        name = str(msg['from']['id']) + '_kibe_sticker.tgs'
                        packname = 'an'+packname[1:]
                    else:
                        await bot.download_file(rmsg['sticker']['file_id'], str(msg['from']['id']) + '_kibe_sticker.tgs')
                        name = str(msg['from']['id']) + '_kibe_sticker.tgs'
                        rsize = True
                if not emoji:
                    emoji = "👍"
                if rsize:
                    name = await resize_photo(name, msg['from']['id'])
                
                try:
                    if anim:
                        await bot.addStickerToSet(user_id=msg['from']['id'], name=packname,
                                              tgs_sticker=open(name, 'rb'), emojis=emoji)
                    else:
                        await bot.addStickerToSet(user_id=msg['from']['id'], name=packname,
                                              png_sticker=open(name, 'rb'), emojis=emoji)
                    success = True
                except TelegramError as e:
                    if e.description == "Bad Request: STICKERSET_INVALID":
                        success = await make_pack(msg, bot, name, anim, packname, emoji)
                        if not success:
                            return await bot.sendMessage(msg['chat']['id'], 'An error has occurred.' ,
                                              reply_to_message_id=msg['message_id'])
                    elif e.description == "Internal Server Error: sticker set not found":
                        success = True
                    else:
                        await bot.sendMessage(msg['chat']['id'], 'Error: ' + e.description,
                                              reply_to_message_id=msg['message_id'])
                        return
                finally:
                    os.remove(name)
                    pass
                if success:
                    await bot.sendMessage(msg['chat']['id'],
                                          "Sticker successfully added to [pack](t.me/addstickers/%s)" % packname,
                                          parse_mode='markdown', reply_to_message_id=msg['message_id'])
                else:
                    await bot.sendMessage(msg['chat']['id'], "Please reply to a sticker for me to kibe it.")
                return True

async def make_pack(msg, bot, sname, anim, packname, emoji):
    user = msg['from']
    name = user['first_name']
    name = name[:50]
    try:
        if anim:
            success = await bot.createNewStickerSet(user['id'], packname, name + "'s Kibe @AmanoTeam",
                                                tgs_sticker=open(sname, 'rb'),
                                                emojis=emoji)
        else:
            success = await bot.createNewStickerSet(user['id'], packname, name + "'s Kibe @AmanoTeam",
                                                png_sticker=open(sname, 'rb'),
                                                emojis=emoji)
    except TelegramError as e:
        success = False
    return success

async def resize_photo(photo, uid):
    """ Resize the given photo to 512x512 """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    os.remove(photo)

    image.save(f'{uid}_kibe_sticker.png')

    return f'{uid}_kibe_sticker.png'