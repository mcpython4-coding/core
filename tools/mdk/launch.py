"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import subprocess
import sys
import json
import os

local = os.path.dirname(__file__)

with open(local+"/config.json") as f:
    data = json.load(f)

print("launching from '{}'".format(data["path"]+"/__main__.py"))

subprocess.call([sys.executable, data["path"]+"/__main__.py", "--addmodfile", local+"/source",
                 "--home-folder", data["home"], "--build-folder", data["build"]]+sys.argv[1:])

