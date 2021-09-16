"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import os
import shutil
import sys
import zipfile

import requests

home = os.path.dirname(__file__).replace("\\", "/").removesuffix("/")
target = home if not os.path.exists(home + "/tools") else home + "/tools"
url = input("url to source: ") if len(sys.argv) == 1 else sys.argv[1]

root = os.path.dirname(home)


print("downloading assets zipfile to {}...".format(root + "/source.zip"))
# todo: with progress bar
r = requests.get(url)
with open(root + "/source.zip", "wb") as f:
    f.write(r.content)
