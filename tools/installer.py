"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import subprocess
import sys
import os

"""
Installation code for setting up your python
Does some magic for stripped builds
"""

home = os.path.dirname(__file__)
if not os.path.exists(home + "/__main__.py"):
    home = os.path.dirname(home)


subprocess.call(
    [sys.executable, "-m", "pip", "install", "-r", home + "/requirements.txt"],
    stdout=sys.stdout,
    stderr=sys.stderr,
)

# todo: move to config the url
subprocess.call(
    [
        sys.executable,
        home + "/tools/update_asset_source.py"
        if os.path.exists(home + "/tools/update_asset_source.py")
        else home + "/update_asset_source.py",
        "https://launcher.mojang.com/v1/objects/8230cf2349b48ba79b0581a3fc76be53f26312bc/client.jar",
        home,
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
