# Copyright (C) 2018-2019 Amano Team <contact@amanoteam.ml>
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

from amanobot.exception import TelegramError
from amanobot.namedtuple import InlineKeyboardMarkup

from config import bot, bot_username


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
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                user = msg['from']
                file_id = msg['reply_to_message']['sticker']['file_id']
                await bot.download_file(file_id, str(msg['from']['id']) + '_kibe_sticker.png')
                packname = "a" + str(user['id']) + "_by_" + bot_username
                if len(msg['text'][5:]) > 0:
                    sticker_emoji = msg['text'].split()[1]
                else:
                    try:
                        sticker_emoji = msg['reply_to_message']['sticker']['emoji']
                    except KeyError:
                        os.remove(str(msg['from']['id']) + "_kibe_sticker.png")
                        return await bot.sendMessage(msg['chat']['id'],
                                                     'You need to define a emoticon for this sticker, since it doesn\'t have one.',
                                                     reply_to_message_id=msg['message_id'])
                success = False
                try:
                    await bot.addStickerToSet(user_id=user['id'], name=packname,
                                              png_sticker=open(str(msg['from']['id']) + '_kibe_sticker.png', 'rb'),
                                              emojis=sticker_emoji)
                    success = True
                except TelegramError as e:
                    if e.description == "Bad Request: STICKERSET_INVALID":
                        await bot.sendMessage(msg['chat']['id'], "Use /make_kibe to create a pack first.",
                                              reply_to_message_id=msg['message_id'])
                        return
                    elif e.description == "Internal Server Error: sticker set not found":
                        success = True
                    else:
                        await bot.sendMessage(msg['chat']['id'], 'Error: ' + e.description,
                                              reply_to_message_id=msg['message_id'])
                        return
                finally:
                    os.remove(str(msg['from']['id']) + "_kibe_sticker.png")

                if success:
                    await bot.sendMessage(msg['chat']['id'],
                                          "Sticker successfully added to [pack](t.me/addstickers/%s)" % packname,
                                          parse_mode='markdown', reply_to_message_id=msg['message_id'])

            else:
                await bot.sendMessage(msg['chat']['id'], "Please reply to a sticker for me to kibe it.")
            return True


        elif msg['text'].startswith('/make_kibe') or msg['text'].startswith('!make_kibe'):
            user = msg['from']
            name = user['first_name']
            name = name[:50]
            packname = "a" + str(user['id']) + "_by_" + bot_username
            success = False
            try:
                success = await bot.createNewStickerSet(user['id'], packname, name + "'s Kibe @AmanoTeam",
                                                        png_sticker="https://i.imgur.com/wB1iZFI.png",
                                                        emojis='©')
            except TelegramError as e:
                if e.description == "Bad Request: sticker set name is already occupied":
                    await bot.sendMessage(msg['chat']['id'],
                                          "Your pack can be found [here](t.me/addstickers/%s)" % packname,
                                          parse_mode='markdown', reply_to_message_id=msg['message_id'])
                elif e.description == "Bad Request: PEER_ID_INVALID":
                    await bot.sendMessage(msg['chat']['id'], "Contact me in PM first.",
                                          reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                              [dict(text='Start', url="t.me/{}".format(bot_username))]]),
                                          reply_to_message_id=msg['message_id'])
                else:
                    await bot.sendMessage(msg['chat']['id'],
                                          "Failed to create sticker pack. Possibly due to blek mejik.\n\n" + str(e),
                                          reply_to_message_id=msg['message_id'])

            if success:
                await bot.sendMessage(msg['chat']['id'],
                                      "Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname,
                                      parse_mode='markdown', reply_to_message_id=msg['message_id'])
            return True
