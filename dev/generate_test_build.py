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

import simplejson as json

import generate_build

local = os.path.dirname(__file__)
home = os.path.dirname(local)

with open(home + "/version.json") as f:
    data = json.load(f)


name = data["name"]
counter = data["preview_build_counter"] + 1
data["preview_build_counter"] += 1
data["id"] += 1


with open(home + "/version.json", mode="w") as f:
    json.dump(data, f, indent="  ")

generate_build.main(" ".join(name.split(" ")[:-1]) + " " + str(counter))
