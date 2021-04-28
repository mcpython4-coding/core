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
import sys
import importlib
import subprocess
import json


local = os.path.dirname(__file__)


sys.path.append(os.path.dirname(local))


if __name__ == "__main__":
    print("mcpython 4 test environment loading...")
    print("WARNING: this system is highly experimental!")

    data = []

    for file in os.listdir(local + "/definitions"):
        if not os.path.exists(local + "/definitions/" + file + "/index.json"):
            continue

        with open(local + "/definitions/" + file + "/index.json") as f:
            config = json.load(f)

        print(f"- found test environment '{config['name']}'")
        # lowest priority is executed last
        data.append((file, -config["priority"], config))

    data.sort(key=lambda e: e[1])

    for file, _, config in data:
        print(
            f"Launching test environment '{config['name']}'. The following lines are defined be the environment"
        )

        importlib.import_module(f"definitions.{file}.main").launch(config)
