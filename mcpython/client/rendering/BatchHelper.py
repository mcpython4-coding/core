"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import typing


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
