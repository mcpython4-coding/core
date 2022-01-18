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

from mcpython import shared
from mcpython.mixin.CodeOptimiser import optimise_code
from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper

shared.IS_TEST_ENV = True

from mcpython.mixin.InstructionMatchers import CounterMatcher
from mcpython.mixin.Mixin import MixinHandler
from tests.util import TestCase


class TestPostInjectionOptimiser(TestCase):
    def setUp(self):
        MixinHandler.LOCKED = False
        shared.IS_TEST_ENV = False

    def test_optimiser_1(self):
        def test():
            a = 0
            del a

        helper = MixinPatchHelper(test)
        optimise_code(helper)

        self.assertEqual(helper.instruction_listing[0].opname, "LOAD_CONST")
        self.assertEqual(helper.instruction_listing[0].argval, None)
        self.assertEqual(helper.instruction_listing[1].opname, "RETURN_VALUE")

        # Integrity check of the bytecode
        self.assertEqual(test(), None)

    def test_basic(self):
        invoked = 0

        def target(flag):
            # only here to make cell var integrity happy
            # should be stripped away during optimiser stage
            invoked

            # should also be stripped away, this is global access
            global shared
            shared

            # Should also be stripped away, is side effect free assignment
            shared = shared

            if flag:
                return 0
            return 1

        handler = MixinHandler()
        handler.makeFunctionArrival("test", target)

        @handler.inject_at_tail("test", inline=True)
        def inject():
            nonlocal invoked
            invoked = 4

        self.assertEqual(target(False), 1)
        self.assertEqual(invoked, 0)
        self.assertEqual(target(True), 0)
        self.assertEqual(invoked, 0)

        # Will apply the later mixin first, as it is optional, and as such can break when overriding it
        handler.applyMixins()

        self.assertEqual(target(True), 0)
        self.assertEqual(invoked, 0)
        self.assertEqual(target(False), 1)
        self.assertEqual(invoked, 4)

        # Check if it is optimised away
        helper = MixinPatchHelper(target)
        self.assertEqual(helper.instruction_listing[0].opname, "LOAD_FAST")
        self.assertEqual(
            helper.instruction_listing[0].arg,
            helper.patcher.ensureVarName("flag"),
            helper.instruction_listing[0],
        )

    def test_attribute2constant_cleanup(self):
        def target(c):
            return c.test_attribute2constant_cleanup

        handler = MixinHandler()
        handler.makeFunctionArrival("test", target)
        handler.replace_attribute_with_constant(
            "test", "%.test_attribute2constant_cleanup", 2
        )
        handler.applyMixins()

        helper = MixinPatchHelper(target)
        self.assertEqual(helper.instruction_listing[0].opname, "LOAD_CONST")
        self.assertEqual(helper.instruction_listing[0].argval, 2)
