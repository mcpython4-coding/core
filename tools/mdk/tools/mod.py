"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import sys
import os


@shared.mod_loader("{NAME}", "stage:mod:init")
def init():
    # Do here your combined factory stuff...
    @shared.mod_loader("{NAME}", "stage:combined_factory:blocks")
    def load_combined_factories():
        pass

    # ... and do here manual block registering ...
    @shared.mod_loader("{NAME}", "stage:block:factory_usage")
    def load_block_factories():
        pass

    # ... and here the items!
    @shared.mod_loader("{NAME}", "stage:item:factory_usage")
    def load_item_factories():
        pass
