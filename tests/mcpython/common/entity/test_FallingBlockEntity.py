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
from unittest import TestCase

from mcpython import shared

shared.IS_TEST_ENV = True


class FakeChunk:
    position = 0, 0

    @classmethod
    def get_block(cls, position):
        return

    @classmethod
    def get_dimension(cls):
        return cls

    @classmethod
    def get_dimension_id(cls):
        return 0


class TestFallingBlockEntity(TestCase):
    def test_module_import(self):
        import mcpython.common.entity.FallingBlockEntity

    def test_tick_despawn(self):
        import mcpython.common.entity.FallingBlockEntity

        instance = mcpython.common.entity.FallingBlockEntity.FallingBlockEntity()

        self.assertFalse(instance.dead)

        instance.tick(0.02)

        self.assertTrue(instance.dead)

    def test_tick_fall(self):
        import mcpython.common.entity.FallingBlockEntity

        instance = mcpython.common.entity.FallingBlockEntity.FallingBlockEntity(
            representing_block="minecraft:stone"
        )
        instance.chunk = FakeChunk

        self.assertFalse(instance.dead)

        instance.tick(0.02)

        self.assertFalse(instance.dead)
        # They have fallen a bit...
        self.assertEqual(instance.position, (0, -0.4, 0))
