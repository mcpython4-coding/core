from unittest import TestCase

from mcpython import shared
shared.IS_TEST_ENV = True


class TestAbstractEntity(TestCase):
    def test_package_import(self):
        import mcpython.common.entity.AbstractEntity
