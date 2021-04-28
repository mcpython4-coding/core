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
import subprocess
import sys
import os

"""
Installation code for setting up your python
Does some magic for stripped builds
"""
IS_DEV = True

home = os.path.dirname(__file__)
if not os.path.exists(home + "/__main__.py"):
    home = os.path.dirname(home)


subprocess.call(
    [sys.executable, "-m", "pip", "install", "-r", home + "/requirements.txt"],
    stdout=sys.stdout,
    stderr=sys.stderr,
)

# todo: move the url to config
subprocess.call(
    [
        sys.executable,
        home + "/tools/update_asset_source.py",
        "https://launcher.mojang.com/v1/objects/6f0597c8dfef133d59cdce2c629a37f0e259512b/client.jar",
        home if not IS_DEV else home + "/resources/source",
    ],
    stdout=sys.stdout,
)

# THE FOLLOWING LINE IS  O N L Y  PRESENT IN DEV ENVIRONMENT
subprocess.call(
    [
        sys.executable,
        home + "/__main__.py",
        "--data-gen",
        "--exit-after-data-gen",
        "--no-window",
    ],
    stdout=sys.stdout,
)
