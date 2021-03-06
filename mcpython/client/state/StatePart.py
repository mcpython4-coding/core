"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StatePart:
    NAME = "null"

    def __init__(self):
        self.part_dict = {}
        self.parts = self.get_sub_parts()
        self.master = None

    def activate(self):
        for part in self.parts:
            part.activate()

    def deactivate(self):
        for part in self.parts:
            part.deactivate()

    def get_sub_parts(self) -> list:
        return []

    def bind_to_eventbus(self):
        for part in self.parts:
            part.master = self.master + [self]
            part.bind_to_eventbus()
