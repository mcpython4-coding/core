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
import dis
import typing

import test_mcpython.mixin
from mcpython.mixin.util import PyOpcodes
from util import TestCase


class TestBasicBytecodeHelpers(TestCase):
    def test_mixin_static_method_call(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        def localtest():
            return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertStaticMethodCallAt(
            0, "test_mcpython.mixin.test_space:test_for_invoke"
        )
        helper.store()
        patcher.applyPatches()

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 1)
        test_mcpython.mixin.test_space.INVOKED = 0

    def test_mixin_static_method_call_twice(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        def localtest():
            return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertStaticMethodCallAt(
            0, "test_mcpython.mixin.test_space:test_for_invoke"
        )
        helper.insertStaticMethodCallAt(
            0, "test_mcpython.mixin.test_space:test_for_invoke"
        )
        helper.store()
        patcher.applyPatches()

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 2)
        test_mcpython.mixin.test_space.INVOKED = 0

    async def test_mixin_static_method_call_to_async(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        async def localtest():
            return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertAsyncStaticMethodCallAt(
            0, "test_mcpython.mixin.test_space:test_for_invoke_async"
        )
        helper.store()
        patcher.applyPatches()

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(await localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 1)
        test_mcpython.mixin.test_space.INVOKED = 0

    async def test_mixin_static_method_call_to_async_twice(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        async def localtest():
            return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertAsyncStaticMethodCallAt(
            0, "test_mcpython.mixin.test_space:test_for_invoke_async"
        )
        helper.insertAsyncStaticMethodCallAt(
            0, "test_mcpython.mixin.test_space:test_for_invoke_async"
        )
        helper.store()
        patcher.applyPatches()

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(await localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 2)
        test_mcpython.mixin.test_space.INVOKED = 0

    async def test_mixin_static_method_call_async_context(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        async def localtest():
            return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertStaticMethodCallAt(
            1, "test_mcpython.mixin.test_space:test_for_invoke"
        )
        helper.store()
        patcher.applyPatches()

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(await localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 1)
        test_mcpython.mixin.test_space.INVOKED = 0

    async def test_mixin_static_method_call_async_context_twice(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        async def localtest():
            return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertStaticMethodCallAt(
            1, "test_mcpython.mixin.test_space:test_for_invoke"
        )
        helper.insertStaticMethodCallAt(
            1, "test_mcpython.mixin.test_space:test_for_invoke"
        )
        helper.store()
        patcher.applyPatches()

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(await localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 2)
        test_mcpython.mixin.test_space.INVOKED = 0

    def test_insertRegion_offset(self):
        from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper

        def test():
            a = 0
            return a

        helper = MixinPatchHelper(test)

        helper.insertRegion(
            1,
            [
                dis.Instruction(
                    "YIELD_VALUE", PyOpcodes.YIELD_VALUE, 0, 0, "", 0, 0, False
                )
            ],
        )

        self.assertEqual(helper.instruction_listing[1].opname, "YIELD_VALUE")
