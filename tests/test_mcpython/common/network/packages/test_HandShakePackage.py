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


class FakeWorld:
    @classmethod
    def add_player(cls, *_, **__):
        pass


class FakeModLoader:
    mods = {}

    @classmethod
    def add_to_add(cls, mod):
        pass


class FakeMod:
    name = "minecraft"
    version = "0.10.0"


class TestClient2ServerHandshake(TestCase):
    def test_module_import(self):
        import mcpython.common.network.packages.HandShakePackage

    def test_setup(self):
        import mcpython.common.config
        from mcpython.common.network.packages.HandShakePackage import (
            Client2ServerHandshake,
        )

        mcpython.common.config.VERSION_ID = 123234

        package = Client2ServerHandshake()
        package.setup("test:player")

        self.assertEqual(package.game_version, 123234)
        self.assertEqual(package.player_name, "test:player")

    def test_serialize(self):
        import mcpython.common.config
        from mcpython.common.network.packages.HandShakePackage import (
            Client2ServerHandshake,
        )
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        mcpython.common.config.VERSION_ID = 123235

        package = Client2ServerHandshake()
        package.setup("test:player")

        buffer = WriteBuffer()
        package.write_to_buffer(buffer)

        package2 = Client2ServerHandshake()
        package2.read_from_buffer(ReadBuffer(buffer.get_data()))

        self.assertEqual(package2.player_name, "test:player")
        self.assertEqual(package2.game_version, 123235)

    def test_handle_inner_compatible(self):
        from mcpython import shared
        from mcpython.common.network.packages.HandShakePackage import (
            Client2ServerHandshake,
            Server2ClientHandshake,
        )

        handshake_back = None

        def answer(p):
            if isinstance(p, Server2ClientHandshake):
                nonlocal handshake_back
                handshake_back = p

        shared.world = FakeWorld
        shared.mod_loader = FakeModLoader

        package = Client2ServerHandshake()
        package.setup("test:player")
        package.answer = answer

        package.handle_inner()

        self.assertIsNotNone(handshake_back)
        self.assertTrue(handshake_back.accept_connection)
        # todo: can we check more?

    def test_handle_inner_incompatible(self):
        import mcpython.common.config
        from mcpython import shared
        from mcpython.common.network.packages.HandShakePackage import (
            Client2ServerHandshake,
            Server2ClientHandshake,
        )

        handshake_back = None

        def answer(p):
            if isinstance(p, Server2ClientHandshake):
                nonlocal handshake_back
                handshake_back = p

        shared.world = FakeWorld
        shared.mod_loader = FakeModLoader

        package = Client2ServerHandshake()
        package.setup("test:player")
        package.answer = answer

        mcpython.common.config.VERSION_ID += 3

        package.handle_inner()

        self.assertIsNotNone(handshake_back)
        self.assertFalse(handshake_back.accept_connection)


class TestServer2ClientHandshake(TestCase):
    def test_setup_deny(self):
        from mcpython import shared
        from mcpython.common.network.packages.HandShakePackage import (
            Server2ClientHandshake,
        )

        shared.mod_loader = FakeModLoader
        FakeModLoader.mods = {"minecraft": FakeMod}

        package = Server2ClientHandshake().setup_deny("test:reason")

        self.assertFalse(package.accept_connection)
        self.assertEqual(package.deny_reason, "test:reason")
        self.assertEqual(package.mod_list, [])
        FakeModLoader.mods.clear()

    def test_setup_accept(self):
        from mcpython import shared
        from mcpython.common.network.packages.HandShakePackage import (
            Server2ClientHandshake,
        )

        shared.mod_loader = FakeModLoader
        FakeModLoader.mods = {"minecraft": FakeMod}

        package = Server2ClientHandshake().setup_accept()

        self.assertTrue(package.accept_connection)
        self.assertEqual(package.deny_reason, "")
        self.assertEqual(package.mod_list, [("minecraft", "0.10.0")])

        FakeModLoader.mods.clear()

    def test_serialize_deny(self):
        from mcpython import shared
        from mcpython.common.network.packages.HandShakePackage import (
            Server2ClientHandshake,
        )
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        shared.mod_loader = FakeModLoader
        FakeModLoader.mods = {"minecraft": FakeMod}

        package = Server2ClientHandshake().setup_deny("test:reason")

        buffer = WriteBuffer()
        package.write_to_buffer(buffer)
        package = Server2ClientHandshake()
        package.read_from_buffer(ReadBuffer(buffer.get_data()))

        self.assertFalse(package.accept_connection)
        self.assertEqual(package.deny_reason, "test:reason")
        self.assertEqual(package.mod_list, [])
        FakeModLoader.mods.clear()

    def test_serialize_accept(self):
        from mcpython import shared
        from mcpython.common.network.packages.HandShakePackage import (
            Server2ClientHandshake,
        )
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        shared.mod_loader = FakeModLoader
        FakeModLoader.mods = {"minecraft": FakeMod}

        package = Server2ClientHandshake().setup_accept()

        buffer = WriteBuffer()
        package.write_to_buffer(buffer)
        package = Server2ClientHandshake()
        package.read_from_buffer(ReadBuffer(buffer.get_data()))

        self.assertTrue(package.accept_connection)
        self.assertEqual(package.deny_reason, "")
        self.assertEqual(package.mod_list, [("minecraft", "0.10.0")])

        FakeModLoader.mods.clear()

    def test_handle_inner(self):
        pass  # todo: implement
