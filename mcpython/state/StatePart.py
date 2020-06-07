"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G


class StatePart:
    NAME = "null"

    def __init__(self):
        self.part_dict = {}
        self.parts = self.get_sub_parts()  # todo: remove
        self.master = None

    def activate(self):
        for statepart in self.parts:
            statepart.activate()

    def deactivate(self):
        for statepart in self.parts:
            statepart.deactivate()

    def get_sub_parts(self) -> list:  # todo: remove
        return []

    def bind_to_eventbus(self):
        for statepart in self.parts:
            statepart.master = self.master + [self]
            statepart.bind_to_eventbus()
