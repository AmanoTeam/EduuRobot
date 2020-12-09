import logging

from pyrogram import Client, idle

from pyrogram.errors.exceptions.bad_request_400 import BadRequest

from config import TOKEN, disabled_plugins, log_chat, API_ID, API_HASH

with open("version.txt") as f:
    version = f.read().strip()


client = Client("bot", API_ID, API_HASH,
                bot_token=TOKEN,
                workers=24,
                plugins=dict(root="plugins", exclude=disabled_plugins))

with client:
    if __name__ == "__main__":
        client.me = client.get_me()
        try:
            client.send_message(log_chat, "**Bot started**\n\n"
                                          f"**Version:** {version}")
        except BadRequest:
            logging.warning("Unable to send message to log_chat.")
        idle()
