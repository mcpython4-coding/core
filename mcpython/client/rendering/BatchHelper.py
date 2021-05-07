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
import typing

from mcpython.util.annotation import onlyInClient


@onlyInClient()
class BatchReference:
    def __init__(self):
        self.delete_able = []
        self.callbacks = []

    def addDeleteAble(self, obj):
        self.delete_able.append(obj)
        return self

    def addCallback(self, function: typing.Callable):
        self.callbacks.append(function)
        return self

    def delete(self):
        [e.delete() for e in self.delete_able]
        [callback() for callback in self.callbacks]
        self.delete_able.clear()
        self.callbacks.clear()
        del self
