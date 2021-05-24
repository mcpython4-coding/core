from unittest import TestCase


class TestAbstractBlock(TestCase):
    def test_module_import(self):
        import mcpython.common.block.AbstractBlock

        self.assertEqual(mcpython.common.block.AbstractBlock.AbstractBlock.TYPE, "minecraft:block_registry")
