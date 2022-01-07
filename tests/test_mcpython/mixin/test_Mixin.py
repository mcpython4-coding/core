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
from unittest import TestCase

import test_mcpython.mixin.test_space


def test():
    return 0


def test_global():
    test()


def reset_test_methods():
    global test, test_global

    def test():
        return 0

    def test_global():
        test()


class TestMixinHandler(TestCase):
    def setUp(self):
        from mcpython.mixin.Mixin import MixinHandler
        MixinHandler.LOCKED = False

    def test_lock(self):
        from mcpython.mixin.Mixin import MixinHandler
        MixinHandler.LOCKED = True
        self.assertRaises(RuntimeError, lambda: MixinHandler("test"))
        MixinHandler.LOCKED = False

    def test_replace_function_body(self):
        from mcpython.mixin.Mixin import MixinHandler
        from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

        handler = MixinHandler("unittest:processor:replace_function_body")

        def test():
            return 0

        @handler.replace_function_body("test")
        def override():
            return 1

        self.assertEqual(test(), 0)

        patcher = FunctionPatcher(test)
        handler.bound_mixin_processors["test"][0][0].apply(handler, patcher, None)
        patcher.applyPatches()

        self.assertEqual(test(), 1)
        reset_test_methods()

    async def test_replace_function_body_async(self):
        from mcpython.mixin.Mixin import MixinHandler
        from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

        handler = MixinHandler("unittest:processor:replace_function_body_async")

        async def test():
            return 0

        @handler.replace_function_body("test")
        async def override():
            return 1

        coro = test()
        self.assertNotEqual(coro, 0)
        self.assertIsInstance(coro, typing.Coroutine)
        self.assertEqual(await coro, 0)

        patcher = FunctionPatcher(test)
        handler.bound_mixin_processors["test"][0][0].apply(handler, patcher, None)
        patcher.applyPatches()

        coro = test()
        self.assertNotEqual(coro, 1)
        self.assertIsInstance(coro, typing.Coroutine)
        self.assertEqual(await coro, 1)
        self.assertEqual(test.__code__.co_code, override.__code__.co_code)
        reset_test_methods()

    def test_function_lookup(self):
        from mcpython.mixin.Mixin import MixinHandler

        method = MixinHandler.lookup_method(
            "tests.test_mcpython.mixin.test_Mixin:TestMixinHandler.test_function_lookup"
        )
        self.assertEqual(method, TestMixinHandler.test_function_lookup)

    def test_mixin_by_name(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin:by_name")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override():
            return 1

        self.assertEqual(test(), 0)
        handler.applyMixins()
        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_mixin_by_name_twice(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin:by_name_twice")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override():
            return 1

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override2():
            return 2

        self.assertEqual(test(), 0)
        handler.applyMixins()
        self.assertEqual(test(), 2)
        reset_test_methods()

    def test_mixin_by_name_twice_with_priority(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin:test_mixin_by_name_twice_with_priority")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test", priority=2)
        def override():
            return 1

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override2():
            return 2

        self.assertEqual(test(), 0)
        handler.applyMixins()
        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_mixin_by_name_twice_with_negative_priority(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin:test_mixin_by_name_twice_with_negative_priority")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override():
            return 1

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test", priority=-1)
        def override2():
            return 2

        self.assertEqual(test(), 0)
        handler.applyMixins()
        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_mixin_by_name_twice_conflicting(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin:test_mixin_by_name_twice_conflicting")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test", priority=2)
        def override():
            return 1

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test", optional=False)
        def override2():
            return 2

        self.assertEqual(test(), 0)

        # This should crash as the second mixin must be applied, but the first one should be applied on top
        # todo: can we do some resolving here, and only apply the second one?
        self.assertRaises(RuntimeError, handler.applyMixins)

        reset_test_methods()

    def test_mixin_by_name_twice_non_conflicting_order(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin:test_mixin_by_name_twice_non_conflicting_order")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test", optional=False)
        def override():
            return 1

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override2():
            return 2

        self.assertEqual(test(), 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overiding it
        handler.applyMixins()

        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_mixin_by_name_twice_conflicting_order(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:mixin:test_mixin_by_name_twice_non_conflicting_order")

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test", optional=False)
        def override():
            return 1

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test", optional=False)
        def override2():
            return 2

        self.assertEqual(test(), 0)

        # Conflicts, as two breaking mixins non-optional cannot co-exist
        self.assertRaises(RuntimeError, handler.applyMixins)

        reset_test_methods()

    def test_constant_replacement_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:processor:replace_constant_1")

        handler.replace_method_constant("tests.test_mcpython.mixin.test_Mixin:test", 0, 1, fail_on_not_found=True)

        self.assertEqual(test(), 0)

        handler.applyMixins()

        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_constant_replacement_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:processor:replace_constant_1")

        handler.replace_method_constant("tests.test_mcpython.mixin.test_Mixin:test", 0, 1, fail_on_not_found=True)
        handler.replace_method_constant("tests.test_mcpython.mixin.test_Mixin:test", 1, 2, fail_on_not_found=True, priority=1)

        self.assertEqual(test(), 0)

        handler.applyMixins()

        self.assertEqual(test(), 2)
        reset_test_methods()

    def test_constant_replacement_fail_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:processor:replace_constant_fail_1")

        handler.replace_method_constant("tests.test_mcpython.mixin.test_Mixin:test", 2, 1, fail_on_not_found=True)

        self.assertEqual(test(), 0)
        self.assertRaises(RuntimeError, handler.applyMixins)

    def test_constant_replacement_fail_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:processor:replace_constant_fail_2")

        handler.replace_method_constant("tests.test_mcpython.mixin.test_Mixin:test", 0, 1, fail_on_not_found=True)
        handler.replace_method_constant("tests.test_mcpython.mixin.test_Mixin:test", 1, 2, fail_on_not_found=True, priority=-1)

        self.assertEqual(test(), 0)
        self.assertRaises(RuntimeError, handler.applyMixins)

    def test_global_to_const_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler("unittest:processor:global2const_1")

        invoked = False

        def callback():
            nonlocal invoked
            invoked = True

        handler.replace_global_with_constant("tests.test_mcpython.mixin.test_Mixin:test_global", "test", callback)

        dis.dis(test_global)
        handler.applyMixins()
        test_global()

        self.assertTrue(invoked)
        reset_test_methods()

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

        coro = sync()
        self.assertNotEqual(coro, 0)
        self.assertIsInstance(coro, typing.Awaitable)
        self.assertEqual(await coro, 0)

    async def makeMethodSync(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        async def sync():
            return 0

        coro = sync()
        self.assertIsInstance(coro, typing.Awaitable)
        self.assertEqual(await coro, 0)

        patcher = FunctionPatcher(sync)
        helper = MixinPatchHelper(patcher)
        helper.makeMethodSync()
        helper.store()
        patcher.applyPatches()

        coro = sync()
        self.assertEqual(coro, 0)
