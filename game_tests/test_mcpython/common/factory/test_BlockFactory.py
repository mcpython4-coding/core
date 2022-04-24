from mcpython.common.block.BlockManager import block_registry
from mcpython.common.factory.BlockFactory import BlockFactory
from mcpython import shared

from game_tests.util import TestCase


class TestBlockFactory(TestCase):
    def test_simple_block(self):
        factory = BlockFactory()
        factory.set_name("minecraft:test_block")
        created = factory.finish()

        block_cls = block_registry["minecraft:test_block"]
        self.assertEqual(block_cls, created)
        self.assertEqual(block_cls.NAME, "minecraft:test_block")

        block_cls = block_registry["test_block"]
        self.assertEqual(block_cls, created)

