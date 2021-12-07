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
import io
from unittest import TestCase


class TestDisconnectionInitPackage(TestCase):
    def test_module_import(self):
        import mcpython.common.network.packages.DisconnectionPackage

    def test_buffer_io(self):
        from mcpython.common.network.packages.DisconnectionPackage import (
            DisconnectionInitPackage,
        )
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        package = DisconnectionInitPackage().set_reason("test reason!")
        self.assertEqual(package.reason, "test reason!")

        buffer = WriteBuffer()
        package.write_to_buffer(buffer)

        buffer = ReadBuffer(io.BytesIO(buffer.get_data()))
        package2 = DisconnectionInitPackage()
        package2.read_from_buffer(buffer)

        self.assertEqual(package.reason, "test reason!")
        self.assertEqual(package.reason, package2.reason)

    async def test_handle_inner(self):
        from mcpython import shared
        from mcpython.common.network.packages.DisconnectionPackage import (
            DisconnectionConfirmPackage,
            DisconnectionInitPackage,
        )

        shared.IS_CLIENT = False

        status_a = False

        def a(p):
            nonlocal status_a
            status_a = isinstance(p, DisconnectionConfirmPackage)

        package = DisconnectionInitPackage().set_reason("test reason!")
        package.answer = a

        await package.handle_inner()

        self.assertTrue(status_a)


# the confirmation package does not need a unit test here, as the underlying systems are hard to test
