import asyncio
import py_compile
from glob import glob
from pyrogram import Client
from pyrogram.session import Session

from config import TOKEN, disabled_plugins

plugins = []

for plugin in glob("plugins/*.py"):
    pluginname = plugin.split("/")[-1].split(".")[0]
    if py_compile.compile(plugin) and pluginname not in disabled_plugins:
        plugins.append(pluginname)
    elif pluginname not in disabled_plugins:
        disabled_plugins.append(pluginname)



client = Client("bot", bot_token=TOKEN, plugins=dict(root="plugins", include=plugins))


if __name__ == "__main__":

    client.run()
