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
from unittest import TestCase, skip


def test():
    return 0


class TestMixinHandler(TestCase):
    def test_replace_function_body(self):
        from mcpython.mixin.Mixin import MixinHandler
        from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

        handler = MixinHandler("unittest:processor")

        def test():
            return 0

        @handler.replace_function_body("test")
        def override():
            return 1

        self.assertEqual(test(), 0)

        patcher = FunctionPatcher(test)
        handler.bound_mixin_processors["test"][0].apply(handler, patcher)
        patcher.applyPatches()

        self.assertEqual(test(), 1)

    def test_function_lookup(self):
        from mcpython.mixin.Mixin import MixinHandler

        method = MixinHandler.lookup_method(
            "tests.test_mcpython.mixin.test_Mixin:TestMixinHandler.test_function_lookup"
        )
        self.assertEqual(method, TestMixinHandler.test_function_lookup)

    def test_mixin_by_name(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override():
            return 1

        self.assertEqual(test(), 0)
        handler.applyMixins()
        self.assertEqual(test(), 1)
