"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

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

subprocess.call(
    [
        sys.executable,
        home + "/tools/update_asset_source.py",
        "https://launcher.mojang.com/v1/objects/ab0d1d122bc2c99daad33befe50a16a07d3b3bf7/client.jar",
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
