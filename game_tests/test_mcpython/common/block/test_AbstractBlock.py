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
from mcpython.util.enums import BlockRotationType, EnumSide

try:
    from pyglet.window import mouse

    SCREEN_ARRIVAL = True
except ImportError:
    SCREEN_ARRIVAL = False
    shared.IS_CLIENT = False


class TestAbstractBlock(TestCase):
    def setUp(self) -> None:
        shared.IS_CLIENT = False
        shared.IS_TEST_ENV = True

    def test_module_import(self):
        import mcpython.common.block.AbstractBlock

        self.assertEqual(
            mcpython.common.block.AbstractBlock.AbstractBlock.TYPE,
            "minecraft:block_registry",
        )

    async def test_network_serializer(self):
        import mcpython.common.block.AbstractBlock
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        class TestBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
            NAME = "minecraft:test_block"

            model_state_set = False

            def get_model_state(self) -> dict:
                return {"test": "test", "tets": "tete23"}

            async def set_model_state(s, state: dict):
                self.assertEqual(state, s.get_model_state())
                TestBlock.model_state_set = True

        buffer = WriteBuffer()
        block = TestBlock()
        await block.write_to_network_buffer(buffer)

        data = buffer.get_data()
        print(data)

        block = TestBlock()
        await block.read_from_network_buffer(ReadBuffer(data))

        self.assertTrue(TestBlock.model_state_set)

    def test_is_solid_method(self):
        import mcpython.common.block.AbstractBlock

        block = mcpython.common.block.AbstractBlock.AbstractBlock()
        for face in EnumSide.iterate():
            self.assertTrue(block.is_face_solid(face), face)

        block = mcpython.common.block.AbstractBlock.AbstractBlock()
        block.face_solid = 0
        for face in EnumSide.iterate():
            self.assertFalse(block.is_face_solid(face), face)

    async def test_get_rotated_variant(self):
        import mcpython.common.block.AbstractBlock

        class Block(mcpython.common.block.AbstractBlock.AbstractBlock):
            def __init__(self):
                super().__init__()
                self.invoked = False

            def get_model_state(self):
                return {"a": "b", "c": "d"}

            async def set_model_state(self_, state: dict):
                self.assertEqual(state, self_.get_model_state())
                self_.invoked = True

        b = Block()
        b2 = await b.get_rotated_variant(BlockRotationType.ROTATE_X_90)
        self.assertIsInstance(b2, Block)
        self.assertTrue(b2.invoked)

    @skipUnless(SCREEN_ARRIVAL, "only when rendering is arrival")
    async def test_on_player_interaction_default_result(self):
        import mcpython.common.block.AbstractBlock

        block = mcpython.common.block.AbstractBlock.AbstractBlock()
        self.assertFalse(
            await block.on_player_interaction(None, mouse.LEFT, 0, (0, 0, 0), None)
        )
