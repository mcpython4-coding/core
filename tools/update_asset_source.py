"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import os
import requests
import zipfile
import shutil
import sys

home = os.path.dirname(__file__).replace("\\", "/")
target = home if not os.path.exists(home + "/tools") else home + "/tools"
url = input("url to source: ") if len(sys.argv) == 1 else sys.argv[1]


print("downloading to {}...".format(target + "/source.zip"))
r = requests.get(url)
with open(target + "/source.zip", "wb") as f:
    f.write(r.content)


print("removing old...")
if os.path.exists(home + "/resources/source"):
    shutil.rmtree(home + "/resources/source")

print("copying new...")

target = sys.argv[2] + "/" if len(sys.argv) > 2 else home + "/resources/source/"

with zipfile.ZipFile(target + "/source.zip") as f:
    for file in f.namelist():
        if "assets" in file or "data" in file and "net/minecraft" not in file:
            data = f.read(file)
            fd = target + file
            d = os.path.dirname(fd)
            if not os.path.isdir(d):
                os.makedirs(d)

            with open(fd, mode="wb") as f2:
                f2.write(data)
