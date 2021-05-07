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
import json
import os
import subprocess
import sys

local = os.path.dirname(__file__)

with open(local + "/config.json") as f:
    data = json.load(f)

print("launching from '{}'".format(data["path"] + "/__main__.py"))

subprocess.call(
    [
        sys.executable,
        data["path"] + "/__main__.py",
        "--add-mod-file",
        local + "/source",
        "--home-folder",
        data["home"],
        "--build-folder",
        data["build"],
    ]
    + sys.argv[1:]
)
