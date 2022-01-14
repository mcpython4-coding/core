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

from mcpython.mixin.InstructionMatchers import CounterMatcher
from tests.util import TestCase

INVOKER_COUNTER = 0
INVOKED = False


def increase_counter():
    global INVOKER_COUNTER
    INVOKER_COUNTER += 1


def test():
    return 0


def test2():
    yield 0


def test3(a):
    return a


def test4(a):
    yield a


def test_global():
    test()


def test_global2():
    test()
    test_global()


def test_global3():
    test()
    test()


def reset_test_methods():
    global test, test2, test3, te4, test_global, test_global2, test_global3

    def test():
        return 0

    def test2():
        yield 0

    def test3(a):
        return a

    def test4(a):
        yield a

    def test_global():
        test()

    def test_global2():
        test()
        test_global()

    def test_global3():
        test()
        test()

    global INVOKED
    INVOKED = 0


class TestMixinHandler(TestCase):
    def setUp(self):
        from mcpython import shared

        shared.IS_TEST_ENV = True

        from mcpython.mixin.Mixin import MixinHandler

        MixinHandler.LOCKED = False

    def test_lock(self):
        from mcpython.mixin.Mixin import MixinHandler

        MixinHandler.LOCKED = True
        self.assertRaises(RuntimeError, lambda: MixinHandler())
        MixinHandler.LOCKED = False

    def test_replace_function_body(self):
        from mcpython.mixin.Mixin import MixinHandler
        from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

        handler = MixinHandler()

        def test():
            return 0

        handler.makeFunctionArrival("test", test)

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

        handler = MixinHandler()

        async def test():
            return 0

        handler.makeFunctionArrival("test", test)

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

        method = MixinHandler().lookup_method(
            "tests.test_mcpython.mixin.test_Mixin:TestMixinHandler.test_function_lookup"
        )
        self.assertEqual(method, TestMixinHandler.test_function_lookup)

    def test_mixin_override(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override():
            return 1

        self.assertEqual(test(), 0)
        handler.applyMixins()
        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_mixin_override_twice(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

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

        handler = MixinHandler()

        @handler.replace_function_body(
            "tests.test_mcpython.mixin.test_Mixin:test", priority=2
        )
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

        handler = MixinHandler()

        @handler.replace_function_body("tests.test_mcpython.mixin.test_Mixin:test")
        def override():
            return 1

        @handler.replace_function_body(
            "tests.test_mcpython.mixin.test_Mixin:test", priority=-1
        )
        def override2():
            return 2

        self.assertEqual(test(), 0)
        handler.applyMixins()
        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_mixin_by_name_twice_conflicting(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        @handler.replace_function_body(
            "tests.test_mcpython.mixin.test_Mixin:test", priority=2
        )
        def override():
            return 1

        @handler.replace_function_body(
            "tests.test_mcpython.mixin.test_Mixin:test", optional=False
        )
        def override2():
            return 2

        self.assertEqual(test(), 0)

        # This should crash as the second mixin must be applied, but the first one should be applied on top
        # todo: can we do some resolving here, and only apply the second one?
        self.assertRaises(RuntimeError, handler.applyMixins)

        reset_test_methods()

    def test_mixin_by_name_twice_non_conflicting_order(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        @handler.replace_function_body(
            "tests.test_mcpython.mixin.test_Mixin:test", optional=False
        )
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

        handler = MixinHandler()

        @handler.replace_function_body(
            "tests.test_mcpython.mixin.test_Mixin:test", optional=False
        )
        def override():
            return 1

        @handler.replace_function_body(
            "tests.test_mcpython.mixin.test_Mixin:test", optional=False
        )
        def override2():
            return 2

        self.assertEqual(test(), 0)

        # Conflicts, as two breaking mixins non-optional cannot co-exist
        self.assertRaises(RuntimeError, handler.applyMixins)

        reset_test_methods()

    def test_constant_replacement_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        handler.replace_method_constant(
            "tests.test_mcpython.mixin.test_Mixin:test", 0, 1, fail_on_not_found=True
        )

        self.assertEqual(test(), 0)

        handler.applyMixins()

        self.assertEqual(test(), 1)
        reset_test_methods()

    def test_constant_replacement_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        handler.replace_method_constant(
            "tests.test_mcpython.mixin.test_Mixin:test", 0, 1, fail_on_not_found=True
        )
        handler.replace_method_constant(
            "tests.test_mcpython.mixin.test_Mixin:test",
            1,
            2,
            fail_on_not_found=True,
            priority=1,
        )

        self.assertEqual(test(), 0)

        handler.applyMixins()

        self.assertEqual(test(), 2)
        reset_test_methods()

    def test_constant_replacement_fail_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        handler.replace_method_constant(
            "tests.test_mcpython.mixin.test_Mixin:test", 2, 1, fail_on_not_found=True
        )

        self.assertEqual(test(), 0)
        self.assertRaises(RuntimeError, handler.applyMixins)

    def test_constant_replacement_fail_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        handler.replace_method_constant(
            "tests.test_mcpython.mixin.test_Mixin:test", 0, 1, fail_on_not_found=True
        )
        handler.replace_method_constant(
            "tests.test_mcpython.mixin.test_Mixin:test",
            1,
            2,
            fail_on_not_found=True,
            priority=-1,
        )

        self.assertEqual(test(), 0)
        self.assertRaises(RuntimeError, handler.applyMixins)

    def test_global_to_global_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        handler.replace_global_ref(
            "tests.test_mcpython.mixin.test_Mixin:test_global",
            "test",
            "increase_counter",
        )

        global INVOKER_COUNTER
        INVOKER_COUNTER = 0

        handler.applyMixins()
        test_global()

        self.assertEqual(INVOKER_COUNTER, 1)
        INVOKER_COUNTER = 0

        reset_test_methods()

    def test_global_to_const_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        invoked = False

        def callback():
            nonlocal invoked
            invoked = True

        handler.replace_global_with_constant(
            "tests.test_mcpython.mixin.test_Mixin:test_global", "test", callback
        )

        handler.applyMixins()
        test_global()

        self.assertTrue(invoked)
        reset_test_methods()

    def test_global_to_const_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        invoked = 0

        def callback():
            nonlocal invoked
            invoked += 1

        handler.replace_global_with_constant(
            "tests.test_mcpython.mixin.test_Mixin:test_global2", "test", callback
        )

        handler.applyMixins()
        test_global2()

        self.assertEqual(invoked, 1)
        reset_test_methods()

    def test_global_to_const_3(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        invoked = 0

        def callback():
            nonlocal invoked
            invoked += 1

        handler.replace_global_with_constant(
            "tests.test_mcpython.mixin.test_Mixin:test_global3",
            "test",
            callback,
            matcher=CounterMatcher(1),
        )

        handler.applyMixins()
        test_global3()

        self.assertEqual(invoked, 1)
        reset_test_methods()

    def test_global_to_const_4(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        invoked = 0

        def callback():
            nonlocal invoked
            invoked += 1

        handler.replace_global_with_constant(
            "tests.test_mcpython.mixin.test_Mixin:test_global3",
            "test",
            callback,
            matcher=CounterMatcher(1) & CounterMatcher(1),
        )

        handler.applyMixins()
        test_global3()

        self.assertEqual(invoked, 1)
        reset_test_methods()

    def test_global_to_const_5(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        invoked = 0

        def callback():
            nonlocal invoked
            invoked += 1

        handler.replace_global_with_constant(
            "tests.test_mcpython.mixin.test_Mixin:test_global3",
            "test",
            callback,
            matcher=CounterMatcher(1) | CounterMatcher(1),
        )

        handler.applyMixins()
        test_global3()

        self.assertEqual(invoked, 1)
        reset_test_methods()

    def test_global_to_const_6(self):
        from mcpython.mixin.Mixin import MixinHandler

        handler = MixinHandler()

        invoked = 0

        def callback():
            nonlocal invoked
            invoked += 1

        handler.replace_global_with_constant(
            "tests.test_mcpython.mixin.test_Mixin:test_global3",
            "test",
            callback,
            matcher=~CounterMatcher(1),
        )

        handler.applyMixins()
        test_global3()

        self.assertEqual(invoked, 1)
        reset_test_methods()

    def test_mixin_inject_at_head_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_head("tests.test_mcpython.mixin.test_Mixin:test", args=(3,))
        def inject(c):
            nonlocal invoked
            invoked += c

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 3)
        reset_test_methods()

    def test_mixin_inject_at_head_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_head("tests.test_mcpython.mixin.test_Mixin:test", args=(3,))
        def inject(c):
            nonlocal invoked
            invoked += c

        @handler.inject_at_head("tests.test_mcpython.mixin.test_Mixin:test", args=(5,))
        def inject2(c):
            nonlocal invoked
            invoked += c

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 8)
        reset_test_methods()

    def test_mixin_inject_at_head_inline_1(self):
        from mcpython.mixin.Mixin import MixinHandler, capture_local

        def target():
            a = 3
            return a

        handler = MixinHandler()
        handler.makeFunctionArrival("test", target)

        @handler.inject_at_head("test", inline=True)
        def inject():
            global INVOKED
            INVOKED += capture_local("a")

        global INVOKED
        INVOKED = 0
        self.assertEqual(target(), 3)
        self.assertEqual(INVOKED, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        dis.dis(target)

        INVOKED = 0
        self.assertEqual(target(), 3)
        self.assertEqual(INVOKED, 3)
        INVOKED = 0

    def test_mixin_inject_at_return_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return(
            "tests.test_mcpython.mixin.test_Mixin:test", args=(3,)
        )
        def inject(c):
            nonlocal invoked
            invoked += c

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 3)
        reset_test_methods()

    def test_mixin_inject_at_return_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return(
            "tests.test_mcpython.mixin.test_Mixin:test", args=(3,)
        )
        def inject(c):
            nonlocal invoked
            invoked += c

        @handler.inject_at_return(
            "tests.test_mcpython.mixin.test_Mixin:test", args=(8,)
        )
        def inject2(c):
            nonlocal invoked
            invoked += c

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 11)
        reset_test_methods()

    def test_mixin_inject_at_return_3(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return(
            "tests.test_mcpython.mixin.test_Mixin:test3", collected_locals=("a",)
        )
        def inject(c):
            nonlocal invoked
            invoked += c * 2

        self.assertEqual(test3(2), 2)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test3(3), 3)
        self.assertEqual(invoked, 6)
        reset_test_methods()

    def test_mixin_inject_at_return_4(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return(
            "tests.test_mcpython.mixin.test_Mixin:test3", collected_locals=("a",)
        )
        def inject(c):
            nonlocal invoked
            invoked += c

        @handler.inject_at_return(
            "tests.test_mcpython.mixin.test_Mixin:test3", collected_locals=("a",)
        )
        def inject2(c):
            nonlocal invoked
            invoked += c

        self.assertEqual(test3(4), 4)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test3(4), 4)
        self.assertEqual(invoked, 8)
        reset_test_methods()

    def test_mixin_inject_at_return_5(self):
        from mcpython.mixin.Mixin import MixinHandler

        def target():
            return 4

        reset_test_methods()

        handler = MixinHandler()
        handler.makeFunctionArrival("test", target)

        invoked = 0

        @handler.inject_at_return("test", add_return_value=True)
        def inject(c):
            nonlocal invoked
            invoked = c

        self.assertEqual(target(), 4)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(target(), 4)
        self.assertEqual(invoked, 4)
        reset_test_methods()

    def test_mixin_inject_at_return_inline_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()

        @handler.inject_at_return(
            "tests.test_mcpython.mixin.test_Mixin:test", inline=True
        )
        def inject(c):
            global INVOKED
            INVOKED = 3

        global INVOKED
        INVOKED = 0
        self.assertEqual(test(), 0)
        self.assertEqual(INVOKED, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        INVOKED = 0
        self.assertEqual(test(), 0)
        self.assertEqual(INVOKED, 3)
        reset_test_methods()


    def test_mixin_inject_at_return_value_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return_replacing_return_value(
            "tests.test_mcpython.mixin.test_Mixin:test", args=(3,)
        )
        def inject(c):
            nonlocal invoked
            invoked += c
            return c - 1

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test(), 2)
        self.assertEqual(invoked, 3)
        reset_test_methods()

    def test_mixin_inject_at_return_value_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return_replacing_return_value(
            "tests.test_mcpython.mixin.test_Mixin:test", args=(3,)
        )
        def inject(c):
            nonlocal invoked
            invoked += c
            return c - 3

        @handler.inject_at_return_replacing_return_value(
            "tests.test_mcpython.mixin.test_Mixin:test", args=(8,)
        )
        def inject2(c):
            nonlocal invoked
            invoked += c
            return c + 4

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test(), 0)
        self.assertEqual(invoked, 11)
        reset_test_methods()

    def test_mixin_inject_at_return_value_3(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return_replacing_return_value(
            "tests.test_mcpython.mixin.test_Mixin:test3", collected_locals=("a",)
        )
        def inject(c):
            nonlocal invoked
            invoked += c * 2
            return c - 2

        self.assertEqual(test3(2), 2)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test3(3), 1)
        self.assertEqual(invoked, 6)
        reset_test_methods()

    def test_mixin_inject_at_return_value_4(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_return_replacing_return_value(
            "tests.test_mcpython.mixin.test_Mixin:test3", collected_locals=("a",)
        )
        def inject(c):
            nonlocal invoked
            invoked += c
            return c + 2

        @handler.inject_at_return_replacing_return_value(
            "tests.test_mcpython.mixin.test_Mixin:test3", collected_locals=("a",)
        )
        def inject2(c):
            nonlocal invoked
            invoked += c
            return c - 5

        self.assertEqual(test3(4), 4)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(test3(4), 6)
        self.assertEqual(invoked, 8)
        reset_test_methods()

    def test_mixin_inject_at_yield_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_yield(
            "tests.test_mcpython.mixin.test_Mixin:test2", args=(2,)
        )
        def inject(c, _):
            nonlocal invoked
            invoked += c + 1

        self.assertEqual(next(test2()), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(test2()), 0)
        self.assertEqual(invoked, 3)
        reset_test_methods()

    def test_mixin_inject_at_yield_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_yield(
            "tests.test_mcpython.mixin.test_Mixin:test2", args=(3,)
        )
        def inject(c, _):
            nonlocal invoked
            invoked += c

        @handler.inject_at_yield(
            "tests.test_mcpython.mixin.test_Mixin:test2", args=(8,)
        )
        def inject2(c, _):
            nonlocal invoked
            invoked += c

        self.assertEqual(next(test2()), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(test2()), 0)
        self.assertEqual(invoked, 11)
        reset_test_methods()

    def test_mixin_inject_at_yield_3(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_yield(
            "tests.test_mcpython.mixin.test_Mixin:test4", collected_locals=("a",)
        )
        def inject(_, c):
            nonlocal invoked
            invoked += c * 8 + 1

        self.assertEqual(next(test4(2)), 2)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(test4(4)), 4)
        self.assertEqual(invoked, 33)
        reset_test_methods()

    def test_mixin_inject_at_yield_4(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_yield(
            "tests.test_mcpython.mixin.test_Mixin:test4", collected_locals=("a",)
        )
        def inject(_, c):
            nonlocal invoked
            invoked += c + 1

        @handler.inject_at_yield(
            "tests.test_mcpython.mixin.test_Mixin:test4", collected_locals=("a",)
        )
        def inject2(_, c):
            nonlocal invoked
            invoked += c + 2

        self.assertEqual(next(test4(4)), 4)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(test4(4)), 4)
        self.assertEqual(invoked, 11)
        reset_test_methods()

    def test_mixin_inject_at_yield_5(self):
        from mcpython.mixin.Mixin import MixinHandler

        def target():
            yield 3

        handler = MixinHandler()
        handler.makeFunctionArrival("test", target)
        invoked = 0

        @handler.inject_at_yield("test", add_yield_value=True)
        def inject(v, _):
            nonlocal invoked
            invoked = v

        self.assertEqual(next(target()), 3)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(target()), 3)
        self.assertEqual(invoked, 3)

    def test_mixin_inject_at_yield_6(self):
        from mcpython.mixin.Mixin import MixinHandler

        def target(c):
            yield c

        handler = MixinHandler()
        handler.makeFunctionArrival("test", target)
        invoked = 0

        @handler.inject_at_yield("test", add_yield_value=True)
        def inject(v, _):
            nonlocal invoked
            invoked = v // 4

        self.assertEqual(next(target(100)), 100)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(target(20)), 20)
        self.assertEqual(invoked, 5)

    def test_mixin_inject_at_yield_inline_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()

        @handler.inject_at_yield(
            "tests.test_mcpython.mixin.test_Mixin:test2", inline=True
        )
        def inject(_):
            global INVOKED
            INVOKED = 4

        self.assertEqual(next(test2()), 0)
        self.assertEqual(INVOKED, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(test2()), 0)
        self.assertEqual(INVOKED, 4)
        reset_test_methods()

    def test_mixin_inject_at_yield_value_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_yield_replacing_yield_value(
            "tests.test_mcpython.mixin.test_Mixin:test2", args=(3,)
        )
        def inject(c, _):
            nonlocal invoked
            invoked += c
            return c - 1

        self.assertEqual(next(test2()), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(test2()), 2)
        self.assertEqual(invoked, 3)
        reset_test_methods()

    def test_mixin_inject_at_yield_value_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()
        invoked = 0

        @handler.inject_at_yield_replacing_yield_value(
            "tests.test_mcpython.mixin.test_Mixin:test2", args=(3,)
        )
        def inject(c, _):
            nonlocal invoked
            invoked += c
            return c + 2

        @handler.inject_at_yield_replacing_yield_value(
            "tests.test_mcpython.mixin.test_Mixin:test2", args=(8,)
        )
        def inject2(c, _):
            nonlocal invoked
            invoked += c
            return c - 6

        self.assertEqual(next(test2()), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(next(test2()), 5)
        self.assertEqual(invoked, 11)
        reset_test_methods()

    def test_mixin_inject_at_tail_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        def target(flag):
            if flag:
                return 0
            return 1

        handler = MixinHandler()
        handler.makeFunctionArrival("test", target)

        invoked = 0

        @handler.inject_at_tail("test", add_return_value=True)
        def inject(c):
            nonlocal invoked
            invoked = c

        self.assertEqual(target(False), 1)
        self.assertEqual(invoked, 0)
        self.assertEqual(target(True), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(target(True), 0)
        self.assertEqual(invoked, 0)
        self.assertEqual(target(False), 1)
        self.assertEqual(invoked, 1)

    def test_mixin_given_method_call_inject_1(self):
        from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper

        INVOKED = 0

        def localtest():
            return 0

        def inject(c: int):
            nonlocal INVOKED
            INVOKED += c

        helper = MixinPatchHelper(localtest)
        helper.insertGivenMethodCallAt(0, inject, 1)
        helper.store()
        helper.patcher.applyPatches()

        localtest()
        self.assertEqual(INVOKED, 1)

    def test_mixin_given_method_call_inject_2(self):
        from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper

        INVOKED = 0

        def localtest():
            return 0

        def inject(c: int):
            nonlocal INVOKED
            INVOKED += c

        helper = MixinPatchHelper(localtest)
        helper.insertGivenMethodCallAt(0, inject, 4)
        helper.store()
        helper.patcher.applyPatches()

        localtest()
        self.assertEqual(INVOKED, 4)

    def test_mixin_given_method_call_inject_3(self):
        from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper

        INVOKED = 0

        def localtest():
            return 0

        def inject(c: int):
            nonlocal INVOKED
            INVOKED += c

        helper = MixinPatchHelper(localtest)
        helper.insertGivenMethodCallAt(0, inject, 1)
        helper.insertGivenMethodCallAt(0, inject, 1)
        helper.store()
        helper.patcher.applyPatches()

        localtest()
        self.assertEqual(INVOKED, 2)

    def test_local2constant_transformer_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()

        def func(c):
            return c

        handler.makeFunctionArrival("test", func)
        handler.replace_local_var_with_const("test", "c", 0)

        self.assertEqual(func(2), 2)
        handler.applyMixins()
        self.assertEqual(func(2), 0)

    def test_local_var_modifier_1(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()

        def func(c):
            return c

        handler.makeFunctionArrival("test", func)

        @handler.inject_local_variable_modifier_at("test", CounterMatcher(0), ["c"])
        def inject(c):
            return c + 2,

        self.assertEqual(func(2), 2)
        handler.applyMixins()

        self.assertEqual(func(2), 4)

    def test_local_var_modifier_2(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()

        def func(c):
            return c

        handler.makeFunctionArrival("test", func)

        @handler.inject_local_variable_modifier_at("test", CounterMatcher(0), ["c"])
        def inject(c):
            return "test",

        self.assertEqual(func(2), 2)
        handler.applyMixins()

        self.assertEqual(func(2), "test")

    def test_local_var_modifier_3(self):
        from mcpython.mixin.Mixin import MixinHandler

        reset_test_methods()

        handler = MixinHandler()

        def func(c):
            d = 10
            return c

        handler.makeFunctionArrival("test", func)

        @handler.inject_local_variable_modifier_at(
            "test", CounterMatcher(0), ["c", "d"]
        )
        def inject(c, d):
            return d, c

        self.assertEqual(func(4), 4)
        handler.applyMixins()

        self.assertEqual(func(2), 10)

