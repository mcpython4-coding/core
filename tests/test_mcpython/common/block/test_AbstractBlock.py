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


class TestAbstractBlock(TestCase):
    def test_module_import(self):
        import mcpython.common.block.AbstractBlock

        self.assertEqual(
            mcpython.common.block.AbstractBlock.AbstractBlock.TYPE,
            "minecraft:block_registry",
        )

    def test_network_serializer(self):
        import mcpython.common.block.AbstractBlock
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        class TestBlock(mcpython.common.block.AbstractBlock.AbstractBlock):
            NAME = "minecraft:test_block"

            model_state_set = False

            def get_model_state(self) -> dict:
                return {"test": "test", "tets": "tete23"}

            def set_model_state(s, state: dict):
                self.assertEqual(state, s.get_model_state())
                TestBlock.model_state_set = True

        buffer = WriteBuffer()
        block = TestBlock()
        block.write_to_network_buffer(buffer)

        block = TestBlock()
        block.read_from_network_buffer(ReadBuffer(buffer.get_data()))

        self.assertTrue(TestBlock.model_state_set)
