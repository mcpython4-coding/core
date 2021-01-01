"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import subprocess
import os
import sys
import generate_build
import simplejson as json

local = os.path.dirname(__file__)
home = os.path.dirname(local)


subprocess.call([sys.executable, local + "/update_licence_headers.py"])
subprocess.call([sys.executable, local + "/formatting.py"])
generate_build.BuildManager(input("build name: ")).generate()

with open(home + "/version.json") as f:
    data = json.load(f)

data["name"] = "test build for " + input("version after this release: ") + " 0"
data["preview_build_counter"] = 1

with open(home + "/version.json", mode="w") as f:
    json.dump(data, f, indent="  ")
