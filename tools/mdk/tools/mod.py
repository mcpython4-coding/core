"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals as G
import sys
import os


@G.modloader("{NAME}", "stage:mod:init")
def init():
    @G.modloader("{NAME}", "stage:combined_factory:blocks")
    def load_combined_factories():  # Do here your combined factory stuff...
        pass

    @G.modloader("{NAME}", "stage:block:factory_usage")
    def load_block_factories():  # ... and do here manual block registering ...
        pass

    @G.modloader("{NAME}", "stage:item:factory_usage")
    def load_item_factories():  # ... and here the items!
        pass

