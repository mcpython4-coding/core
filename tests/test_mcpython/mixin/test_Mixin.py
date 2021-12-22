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
from unittest import TestCase

import test_mcpython.mixin.test_space


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

    async def test_replace_function_body_async(self):
        from mcpython.mixin.Mixin import MixinHandler
        from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

        handler = MixinHandler("unittest:processor")

        async def test():
            return 0

        @handler.replace_function_body("test")
        async def override():
            return 1

        self.assertNotEqual(test(), 0)
        self.assertEqual(await test(), 0)

        patcher = FunctionPatcher(test)
        handler.bound_mixin_processors["test"][0].apply(handler, patcher)
        patcher.applyPatches()

        self.assertNotEqual(test(), 1)
        self.assertEqual(await test(), 1)
        self.assertEqual(test.__code__.co_code, override.__code__.co_code)

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

    def test_mixin_static_method_call(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        def localtest():
            return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertStaticMethodCallAt(
            1, "test_mcpython.mixin.test_space:test_for_invoke"
        )
        helper.store()
        patcher.applyPatches()

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 1)

    async def test_mixin_static_method_call_to_async(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        async def localtest():
            return 0

        # async def target():
        #     import test_mcpython.mixin.test_space
        #     await test_mcpython.mixin.test_space.test_for_invoke_async()
        #     return 0

        patcher = FunctionPatcher(localtest)
        helper = MixinPatchHelper(patcher)
        helper.insertAsyncStaticMethodCallAt(
            0, "test_mcpython.mixin.test_space:test_for_invoke_async"
        )
        helper.store()
        patcher.applyPatches()

        # print("compare")
        # dis.dis(target)
        # print("patched")
        # dis.dis(localtest)

        count = test_mcpython.mixin.test_space.INVOKED
        self.assertEqual(await localtest(), 0)
        self.assertEqual(test_mcpython.mixin.test_space.INVOKED, count + 1)

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

    async def makeMethodAsync(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        def sync():
            return 0

        self.assertEqual(sync(), 0)

        patcher = FunctionPatcher(sync)
        helper = MixinPatchHelper(patcher)
        helper.makeMethodAsync()
        helper.store()
        patcher.applyPatches()

        self.assertNotEqual(sync(), 0)
        self.assertEqual(await sync(), 0)
