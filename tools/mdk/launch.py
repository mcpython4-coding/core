"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import subprocess
import sys
import json
import os

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
