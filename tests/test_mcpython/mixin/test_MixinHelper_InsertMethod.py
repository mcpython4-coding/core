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

from util import TestCase


class TestInsertMethod(TestCase):
    def test_insert_method_1(self):
        from mcpython.mixin.MixinMethodWrapper import FunctionPatcher, MixinPatchHelper

        def target():
            return 0

        def test():
            global INVOKED
            INVOKED = True

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(0, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        target()
        self.assertTrue(INVOKED)
        INVOKED = False

    def test_insert_method_local_capture_5(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
        )

        def target():
            a = 1
            b = 2
            return a

        def test():
            x = capture_local("a")
            y = capture_local("b")
            global INVOKED
            INVOKED = x + y
            a = 2

        self.assertEqual(target(), 1)

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(4, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        self.assertEqual(target(), 1, "local protection unsuccessful")
        self.assertEqual(INVOKED, 3)
        INVOKED = False

    def test_insert_method_local_capture_1(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
        )

        def target():
            a = 1
            return 0

        def test():
            x = capture_local("a")
            global INVOKED
            INVOKED = x

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(2, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        target()
        self.assertEqual(INVOKED, 1)
        INVOKED = False

    def test_insert_method_local_capture_2(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
        )

        def target():
            a = 1
            return a

        def test():
            x = capture_local("a")
            global INVOKED
            INVOKED = x
            x = 2

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(2, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        self.assertEqual(target(), 2)
        self.assertEqual(INVOKED, 1)
        INVOKED = False

    def test_insert_method_local_capture_static_2(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local_static,
        )

        def target():
            a = 1
            return a

        def test():
            x = capture_local_static("a")
            global INVOKED
            INVOKED = x
            x = 2

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(2, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        self.assertEqual(target(), 1)
        self.assertEqual(INVOKED, 1)
        INVOKED = False

    def test_insert_method_local_capture_3(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
        )

        def target():
            a = 1
            b = 2
            return a

        def test():
            x = capture_local("a")
            y = capture_local("b")
            global INVOKED
            INVOKED = x + y
            x = 2

        self.assertEqual(target(), 1)

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(4, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        self.assertEqual(
            target(), 2, "local rebind not fully functional; write back failed!"
        )
        self.assertEqual(INVOKED, 3)
        INVOKED = False

    def test_insert_method_local_capture_static_3(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
            capture_local_static,
        )

        def target():
            a = 1
            b = 2
            return a

        def test():
            x = capture_local_static("a")
            y = capture_local("b")
            global INVOKED
            INVOKED = x + y
            x = 2

        self.assertEqual(target(), 1)

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(4, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        self.assertEqual(target(), 1)
        self.assertEqual(INVOKED, 3)
        INVOKED = False

    def test_insert_method_local_capture_4(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
        )

        def target():
            a = 1
            return a

        def test():
            global INVOKED
            INVOKED = capture_local("a")

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(2, FunctionPatcher(test))
        helper.store()
        helper.patcher.applyPatches()

        global INVOKED
        INVOKED = False
        self.assertEqual(target(), 1)
        self.assertEqual(INVOKED, 1)
        INVOKED = False

    def test_mixin_early_exit_1(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            mixin_return,
        )

        def target():
            return 1

        def test():
            mixin_return(0)
            return -1

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(0, test)
        helper.store()
        helper.patcher.applyPatches()

        self.assertEqual(target(), 0)

    def test_mixin_early_exit_2(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
            mixin_return,
        )

        def target(c: bool):
            return 1

        def test():
            a = capture_local("c")
            if a:
                mixin_return(0)

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(0, test)
        helper.store()
        helper.patcher.applyPatches()

        self.assertEqual(target(True), 0)
        self.assertEqual(target(False), 1)

    def test_mixin_early_exit_3(self):
        from mcpython.mixin.MixinMethodWrapper import (
            FunctionPatcher,
            MixinPatchHelper,
            capture_local,
            mixin_return,
        )

        def target(c: bool):
            return c

        def test():
            a = capture_local("c")
            if a:
                mixin_return(0)
            a = 2

        helper = MixinPatchHelper(target)
        helper.insertMethodAt(0, test)
        helper.store()
        helper.patcher.applyPatches()

        self.assertEqual(target(True), 0)
        self.assertEqual(target(False), 2)