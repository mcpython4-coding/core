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
import sys

import requests

home = os.path.dirname(__file__).replace("\\", "/").removesuffix("/")
target = f"{home}/tools" if os.path.exists(f"{home}/tools") else home
url = input("url to source: ") if len(sys.argv) == 1 else sys.argv[1]

root = os.path.dirname(home)


print(f"downloading assets zipfile to {root}/source.zip...")
# todo: with progress bar
r = requests.get(url)
with open(f"{root}/source.zip", "wb") as f:
    f.write(r.content)
