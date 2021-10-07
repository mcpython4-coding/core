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


class TestFunctionPatcher(TestCase):
    def test_apply_patches_simple(self):
        from mcpython.mixin import PyBytecodeManipulator

        value = 0

        class Test:
            def wadd(self, x, y=1):
                pow_n = 3
                result = (x + y) ** pow_n
                nonlocal value
                value = result

        # Create an object of that class so we can be sure that it updates existing object-binds
        test_obj = Test()

        test_obj.wadd(3, 1)
        self.assertEqual(value, 64)

        # Apply a small patch to the function, replacing the + with a - in the code
        obj = PyBytecodeManipulator.FunctionPatcher(Test.wadd)
        obj.code_string[12:13] = dis.opmap["BINARY_SUBTRACT"].to_bytes(
            1, byteorder="little"
        )
        obj.applyPatches()

        value = 0
        test_obj.wadd(3, 1)
        self.assertEqual(value, 1)
