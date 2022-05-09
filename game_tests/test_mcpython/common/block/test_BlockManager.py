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
from game_tests.util import TestCase
from mcpython import shared


class FakeModLoader:
    def add_to_add(self, mod):
        pass

    def __call__(self, *args, **kwargs):
        return lambda func: func


class TestBlockManager(TestCase):
    def test_module_import(self):
        shared.mod_loader = FakeModLoader()

        import mcpython.common.block.BlockManager
