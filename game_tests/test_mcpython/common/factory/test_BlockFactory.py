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
from mcpython.common.block.BlockManager import block_registry
from mcpython.common.factory.BlockFactory import BlockFactory


class TestBlockFactory(TestCase):
    def test_simple_block(self):
        factory = BlockFactory()
        factory.set_name("minecraft:test_block")
        created = factory.finish()

        block_cls = block_registry["minecraft:test_block"]
        self.assertEqual(block_cls, created)
        self.assertEqual(block_cls.NAME, "minecraft:test_block")

        block_cls = block_registry["test_block"]
        self.assertEqual(block_cls, created)
