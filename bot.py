from pyrogram import Client, idle

from config import TOKEN, disabled_plugins, log_chat, API_ID, API_HASH

with open("version.txt") as f:
    version = f.read().strip()

with Client("bot", API_ID, API_HASH, bot_token=TOKEN, plugins=dict(root="plugins", exclude=disabled_plugins)) as client:
    if __name__ == "__main__":
        client.me = client.get_me()
        client.send_message(log_chat, "**Bot started**\n\n"
                                      f"**Version:** {version}")
        idle()
