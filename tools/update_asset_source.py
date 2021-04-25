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
import requests
import zipfile
import shutil
import sys

home = os.path.dirname(__file__).replace("\\", "/").removesuffix("/")
target = home if not os.path.exists(home + "/tools") else home + "/tools"
url = input("url to source: ") if len(sys.argv) == 1 else sys.argv[1]


print("downloading assets zipfile to {}...".format(target + "/source.zip"))
# todo: with progress bar
r = requests.get(url)
with open(target + "/source.zip", "wb") as f:
    f.write(r.content)


if len(sys.argv) > 2:
    target_dir = sys.argv[2]

else:
    target_dir = os.path.dirname(home) + "/resources/source/"
    if os.path.exists(home + "/resources/source"):
        print("removing old...")
        shutil.rmtree(home + "/resources/source")

# todo: can we dynamically link them by writing stuff into e.g. version.json
# todo: with this, can we also link installations from the mc installation?
print(f"extracting assets into {target_dir}...")

with zipfile.ZipFile(target + "/source.zip") as f:
    for file in f.namelist():
        if file.startswith("assets/") or file.startswith("data/"):
            data = f.read(file)
            fd = os.path.join(target_dir, file)
            d = os.path.dirname(fd)
            os.makedirs(d, exist_ok=True)

            with open(fd, mode="wb") as f2:
                f2.write(data)
