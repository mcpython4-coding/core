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
import subprocess
import sys

import isort

# todo: add config option for this
home = os.path.dirname(os.path.dirname(__file__))

for root, dirs, files in os.walk(home):
    if (
        ".git" in root
        or "resources" in root
        or "build" in root
        or "__pycache__" in root
    ):
        continue

    for file in files:
        if not file.endswith(".py"):
            continue

        if file == "LaunchWrapper.py":
            continue

        try:
            isort.file(os.path.join(root, file))
        except:
            print(os.path.join(root, file))
            raise

subprocess.call([sys.executable, "-m", "black", home])
