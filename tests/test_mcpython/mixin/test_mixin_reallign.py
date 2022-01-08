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
from dis import Instruction
from unittest import TestCase

import test_mcpython.mixin.test_space
from mcpython.mixin import PyBytecodeManipulator
from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper
from mcpython.mixin.util import create_instruction
from mcpython.mixin.Mixin import MixinHandler


class TestMixinAlignment(TestCase):
    def setUp(self):
        MixinHandler.LOCKED = False

    def test_simple_remove(self):
        test = False

        def a():
            nonlocal test
            test = True

        patcher = PyBytecodeManipulator.FunctionPatcher(a)
        helper = MixinPatchHelper(patcher)

        a()
        self.assertTrue(test)
        test = False

        helper.deleteRegion(0, 2)
        helper.store()
        patcher.applyPatches()
        a()
        self.assertFalse(test)

    def test_simple_insert(self):
        test = False

        def a():
            pass

        patcher = PyBytecodeManipulator.FunctionPatcher(a)
        helper = MixinPatchHelper(patcher)

        a()
        self.assertFalse(test)

        helper.insertRegion(
            0,
            [
                create_instruction("LOAD_CONST", arg_pt=patcher.ensureConstant(True)),
                create_instruction("RETURN_VALUE"),
            ],
        )
        helper.store()
        patcher.applyPatches()
        # helper.print_stats()
        self.assertEqual(a(), True)

    def test_jump_change(self):
        test1 = False
        test2 = False

        def a(arg):
            if arg:
                nonlocal test1
                test1 = True
            else:
                nonlocal test2
                test2 = True

        a(False)
        self.assertFalse(test1)
        self.assertTrue(test2)
        test2 = False

        a(True)
        self.assertTrue(test1)
        self.assertFalse(test2)
        test1 = False

        patcher = PyBytecodeManipulator.FunctionPatcher(a)
        helper = MixinPatchHelper(patcher)

        # Delete the two instructions storing the True value in test1
        helper.deleteRegion(2, 4)
        helper.store()
        patcher.applyPatches()

        a(False)
        self.assertFalse(test1)
        self.assertTrue(test2)
        test2 = False

        a(True)
        self.assertFalse(test1)
        self.assertFalse(test2)

