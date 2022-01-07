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
from .test_space import create_big_function


class TestBigFunctions(TestCase):
    def test_extended_indices_1(self):
        from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper
        func = create_big_function()
        helper = MixinPatchHelper(func)
        helper.replaceConstant(0, 1)
        helper.store()
        helper.patcher.applyPatches()
        func()

