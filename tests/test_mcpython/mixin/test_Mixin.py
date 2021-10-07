from unittest import TestCase, skip


class TestMixinHandler(TestCase):
    def test_replace_function_body(self):
        from mcpython.mixin.Mixin import MixinHandler
        from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher

        handler = MixinHandler("unittest:processor")

        def test():
            return 0

        @handler.replace_function_body("test")
        def override():
            return 1

        self.assertEqual(test(), 0)

        patcher = FunctionPatcher(test)
        handler.bound_mixin_processors["test"][0].apply(handler, patcher)
        patcher.applyPatches()

        self.assertEqual(test(), 1)

