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
from unittest import skipUnless

from game_tests.util import TestCase
from mcpython import shared
from mcpython.util.enums import EnumSide

try:
    from pyglet.window import mouse

    SCREEN_ARRIVAL = True
except ImportError:
    SCREEN_ARRIVAL = False

shared.IS_CLIENT = True


class Weakable:
    pass


@skipUnless(SCREEN_ARRIVAL, "only when rendering is arrival")
class TestFaceInfo(TestCase):
    def setUp(self) -> None:
        shared.IS_CLIENT = True

    def test_module_import(self):
        import mcpython.common.block.FaceInfo

    def test_constructor(self):
        from mcpython.common.block.FaceInfo import FaceInfo

        block = Weakable()

        info = FaceInfo(block)
        self.assertEqual(info.faces, 0)
        self.assertEqual(info.multi_data, None)
        self.assertIsNone(info.custom_renderer)
        self.assertFalse(info.subscribed_renderer)
        self.assertIsNone(info.multi_data)
        self.assertEqual(info.faces, 0)

    def test_is_shown(self):
        from mcpython.common.block.FaceInfo import FaceInfo

        block = Weakable()

        info = FaceInfo(block)
        self.assertFalse(info.is_shown())

    def test_show_hide_face_custom_renderer(self):
        from mcpython.client.rendering.blocks.ICustomBlockRenderer import (
            ICustomBlockRenderer,
        )
        from mcpython.common.block.FaceInfo import FaceInfo

        block = Weakable()

        class BlockRenderer(ICustomBlockRenderer):
            hit = False
            hit_hide = False

            def on_block_exposed(s, b):
                s.hit = True
                self.assertEqual(b, block)

            def on_block_fully_hidden(s, b):
                s.hit_hide = True
                self.assertEqual(b, block)

        instance = BlockRenderer()

        info = FaceInfo(block)
        info.custom_renderer = instance
        info.show_faces(1)

        self.assertTrue(instance.hit)
        self.assertTrue(info.subscribed_renderer)
        self.assertTrue(info.is_shown())
        self.assertTrue(info.faces & 1)

        info.hide_faces(1)

        self.assertTrue(instance.hit_hide)
        self.assertFalse(info.subscribed_renderer)
        self.assertFalse(info.is_shown())
