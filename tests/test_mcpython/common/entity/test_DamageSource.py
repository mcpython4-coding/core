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
from tests.util import TestCase

from mcpython import shared

shared.IS_TEST_ENV = True


class TestDamageSource(TestCase):
    def test_package_import(self):
        import mcpython.common.entity.DamageSource

    def test_constructor(self):
        import mcpython.common.entity.DamageSource

        source = mcpython.common.entity.DamageSource.DamageSource("minecraft:test")

        self.assertEqual(source.type, "minecraft:test")

    def test_attribute(self):
        import mcpython.common.entity.DamageSource

        source = mcpython.common.entity.DamageSource.DamageSource()
        source.setAttribute("test", "value")
        self.assertEqual(source.getAttribute("test"), "value")

    def test_eq(self):
        import mcpython.common.entity.DamageSource

        source1 = mcpython.common.entity.DamageSource.DamageSource()
        source2 = mcpython.common.entity.DamageSource.DamageSource()
        self.assertEqual(source1, source2)

        source1.setAttribute("test", 1)
        source2.setAttribute("test", 1)
        self.assertEqual(source1, source2)

        source2.setAttribute("test", 5)
        self.assertNotEqual(source1, source2)

        source2.setAttribute("test", 1)
        source2.setAttribute("is_magic", True)
        self.assertNotEqual(source1, source2)

        source1.setAttribute("is_magic", True)
        self.assertEqual(source1, source2)
