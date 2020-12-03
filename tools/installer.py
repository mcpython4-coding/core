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
    [sys.executable, "-m", "pip", "install", "-r", home+"/requirements.txt"],
    stdout=sys.stdout,
    stderr=sys.stderr,
)

subprocess.call(
    [
        sys.executable,
        home + "/tools/update_asset_source.py",
        "https://launcher.mojang.com/v1/objects/818705401f58ee4df2267bf97fa2e0fb6e78ce28/client.jar"
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
