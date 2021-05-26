from unittest import TestCase

from mcpython import shared


class FakeModLoader:
    def add_to_add(self, mod):
        pass

    def __call__(self, *args, **kwargs):
        return lambda func: func


class TestBlockManager(TestCase):
    def test_module_import(self):
        shared.mod_loader = FakeModLoader()

        import mcpython.common.block.BlockManager
