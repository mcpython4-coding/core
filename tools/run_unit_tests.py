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
import subprocess
import sys

local = os.path.dirname(os.path.dirname(__file__))

# This is the command to run all unit tests correctly
result = subprocess.call(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        local + "/game_tests",
        "-t",
        local,
    ],
    cwd=local,
    env=os.environ | {"DISABLE_OPTIMISATION_APPLY": "1"},
)
print("exit code:", result)
sys.exit(result)
