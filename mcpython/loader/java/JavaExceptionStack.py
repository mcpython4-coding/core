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
class StackCollectingException(Exception):
    def __init__(self, text: str, base: Exception = None):
        self.text = text
        self.traces = []
        self.base = base

    def add_trace(self, line: str):
        self.traces.append(line)
        return self

    def format_exception(self):
        return self.text + "\n" + "\n".join(self.traces)
