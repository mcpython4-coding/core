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
from mcpython import shared


class FunctionFile:
    @classmethod
    def from_file(cls, file: str) -> "FunctionFile":
        with open(file) as f:
            lines = f.read().split("\n")

        instance = cls()

        for line in lines:
            line = line.strip()
            if len(line) == 0 or line.startswith("#"):
                continue

            instance.command_nodes.append(
                shared.command_parser.parse(
                    line if not line.startswith("/") else "/" + line
                )
            )

        return instance

    def __init__(self):
        self.command_nodes = []

    def execute(self, info):
        for node, data in self.command_nodes:
            for func in node.on_execution_callbacks:
                func(info, data)
