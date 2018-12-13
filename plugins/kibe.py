import os
from amanobot.namedtuple import InlineKeyboardMarkup
from amanobot.exception import TelegramError
import config

bot = config.bot
bot_username = config.bot_username


def escape_markdown(text):
    text = text.replace('[', '\[')
    text = text.replace('_', '\_')
    text = text.replace('*', '\*')
    text = text.replace('`', '\`')

    return text


def kibe(msg):
    if msg.get('text'):
        if msg['text'].startswith('/kibe_stickerid') or msg['text'].startswith('!stickerid'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                bot.sendMessage(msg['chat']['id'], "Sticker ID:\n```" +
                                msg['reply_to_message']['sticker']['file_id'] + "```",
                                parse_mode='markdown', reply_to_message_id=msg['message_id'])
            else:
                bot.sendMessage(msg['chat']['id'], "Please reply to a sticker to get its ID.")

        elif msg['text'].startswith('/kibe_getsticker') or msg['text'].startswith('!getsticker'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                chat_id = msg['chat']['id']
                file_id = msg['reply_to_message']['sticker']['file_id']
                bot.download_file(file_id, 'sticker.png')
                bot.sendDocument(chat_id, document=open('sticker.png', 'rb'))
                os.remove("sticker.png")
            else:
                bot.sendMessage(msg['chat']['id'], "Please reply to a sticker for me to upload its PNG.",
                                reply_to_message_id=msg['message_id'])

        elif msg['text'].startswith('/kibe') or msg['text'].startswith('!kibe'):
            if msg.get('reply_to_message') and msg['reply_to_message'].get('sticker'):
                user = msg['from']
                file_id = msg['reply_to_message']['sticker']['file_id']
                bot.download_file(file_id, str(msg['from']['id']) + '_kibe_sticker.png')
                packname = "a" + str(user['id']) + "_by_" + config.me['username']
                if len(msg['text'][5:]) > 0:
                    sticker_emoji = msg['text'].split()[1]
                else:
                    try:
                        sticker_emoji = msg['reply_to_message']['sticker']['emoji']
                    except KeyError:
                        return bot.sendMessage(msg['chat']['id'], 'You need to define a emoticon for this sticker, since it doesn\'t have one.',
                                               reply_to_message_id=msg['message_id'])
                success = False
                try:
                    bot.addStickerToSet(user_id=user['id'], name=packname,
                                        png_sticker=open(str(msg['from']['id']) + '_kibe_sticker.png', 'rb'),
                                        emojis=sticker_emoji)
                    success = True
                except TelegramError as e:
                    if e.description == "Bad Request: STICKERSET_INVALID":
                        bot.sendMessage(msg['chat']['id'], "Use /make_kibe to create a pack first.",
                                        reply_to_message_id=msg['message_id'])
                        return
                    elif e.description == "Internal Server Error: sticker set not found":
                        success = True
                finally:
                    os.remove(str(msg['from']['id']) + "_kibe_sticker.png")

                if success:
                    bot.sendMessage(msg['chat']['id'],
                                    "Sticker successfully added to [pack](t.me/addstickers/%s)" % packname,
                                    parse_mode='markdown', reply_to_message_id=msg['message_id'])

            else:
                bot.sendMessage(msg['chat']['id'], "Please reply to a sticker for me to kibe it.")
        elif msg['text'].startswith('/make_kibe') or msg['text'].startswith('!make_kibe'):
            user = msg['from']
            name = user['first_name']
            name = name[:50]
            packname = "a" + str(user['id']) + "_by_" + config.me['username']
            success = False
            try:
                success = bot.createNewStickerSet(user['id'], packname, name + "'s Kibe @AmanoTeam",
                                                  png_sticker="https://i.imgur.com/wB1iZFI.png",
                                                  emojis='©')
            except TelegramError as e:
                if e.description == "Bad Request: sticker set name is already occupied":
                    bot.sendMessage(msg['chat']['id'],
                                    "Your pack can be found [here](t.me/addstickers/%s)" % packname,
                                    parse_mode='markdown', reply_to_message_id=msg['message_id'])
                elif e.description == "Bad Request: PEER_ID_INVALID":
                    bot.sendMessage(msg['chat']['id'], "Contact me in PM first.",
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                        [dict(text='Start', url="t.me/{}".format(config.me['username']))]]),
                                    reply_to_message_id=msg['message_id'])
                else:
                    bot.sendMessage(msg['chat']['id'], "Failed to create sticker pack. Possibly due to blek mejik.",
                                    reply_to_message_id=msg['message_id'])

            if success:
                bot.sendMessage(msg['chat']['id'],
                                "Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname,
                                parse_mode='markdown', reply_to_message_id=msg['message_id'])
