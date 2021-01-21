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
installation code for setting up your python
"""

home = os.path.dirname(os.path.dirname(__file__))


subprocess.call(
    [sys.executable, "-m", "pip", "install", "-r", home + "/requirements.txt"],
    stdout=sys.stdout,
    stderr=sys.stderr,
)

# todo: move to config the url
subprocess.call(
    [
        sys.executable,
        home + "/tools/update_asset_source.py",
        "https://launcher.mojang.com/v1/objects/30d492744e5c282331958d2096cc8b39d8ec3145/client.jar",
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
