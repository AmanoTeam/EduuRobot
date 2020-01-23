import asyncio

from pyrogram import Client

from config import TOKEN, disabled_plugins, log_chat, API_ID, API_HASH

with open("version.txt") as f:
    version = f.read().strip()


async def run_client(client):
    await client.start()
    await client.send_message(log_chat, "**Bot started**\n\n"
                                        f"**Version:** {version}")
    await client.idle()

client = Client("bot", API_ID, API_HASH, bot_token=TOKEN, plugins=dict(root="plugins", exclude=disabled_plugins))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_client(client))
