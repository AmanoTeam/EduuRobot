import asyncio
import py_compile
from glob import glob
from pyrogram import Client

from config import TOKEN, disabled_plugins, log_chat


with open("version.txt") as f:
    version = f.read().strip()


async def run_client(client):
    await client.start()
    await client.send_message(log_chat, "**Bot started**\n\n"
                                        f"**Version:** {version}\n\n"
                                        f"**Loaded plugins:** ({len(plugins)}) {', '.join(plugins)}\n"
                                        f"**Not loaded plugins:** ({len(disabled_plugins)}) {', '.join(disabled_plugins)}")
    await client.idle()


plugins = []

for plugin in glob("plugins/*.py"):
    pluginname = plugin.split("/")[-1].split(".")[0]
    if py_compile.compile(plugin) and pluginname not in disabled_plugins:
        plugins.append(pluginname)
    elif pluginname not in disabled_plugins:
        disabled_plugins.append(pluginname)


client = Client("bot", bot_token=TOKEN, plugins=dict(root="plugins", include=plugins))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_client(client))
