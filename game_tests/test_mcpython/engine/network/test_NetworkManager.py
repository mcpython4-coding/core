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
from game_tests.util import TestCase


class TestNetworkManager(TestCase):
    def test_module_import(self):
        import mcpython.engine.network.NetworkManager

    async def test_reset_package_registry(self):
        from mcpython import shared
        from mcpython.engine.network.NetworkManager import load_packages

        shared.NETWORK_MANAGER.reset_package_registry()

        self.assertEqual(len(shared.NETWORK_MANAGER.package_types), 0)

        await load_packages()

        self.assertNotEqual(len(shared.NETWORK_MANAGER.package_types), 0)

        shared.NETWORK_MANAGER.reset_package_registry()

        self.assertEqual(len(shared.NETWORK_MANAGER.package_types), 0)

    async def test_dynamic_id_info_1(self):
        from mcpython import shared
        from mcpython.engine.network.NetworkManager import load_packages

        await load_packages()

        data = list(shared.NETWORK_MANAGER.get_dynamic_id_info())

        await shared.NETWORK_MANAGER.set_dynamic_id_info(data)

        self.assertNotEqual(len(shared.NETWORK_MANAGER.package_types), 0)

        # todo: can we do more?

        shared.NETWORK_MANAGER.reset_package_registry()

    async def test_dynamic_id_info_2(self):
        from mcpython import shared

        shared.IS_TEST_ENV = True

        from mcpython.engine.network.AbstractPackage import AbstractPackage
        from mcpython.engine.network.NetworkManager import load_packages

        class TestPackage(AbstractPackage):
            PACKAGE_NAME = "minecraft:test_package"

        shared.NETWORK_MANAGER.register_package_type(TestPackage)
        await load_packages()

        data = list(shared.NETWORK_MANAGER.get_dynamic_id_info())

        shared.NETWORK_MANAGER.reset_package_registry()
        await load_packages()

        await shared.NETWORK_MANAGER.set_dynamic_id_info(data)

        self.assertNotEqual(len(shared.NETWORK_MANAGER.package_types), 0)

        print(shared.NETWORK_MANAGER.package_types)

        # todo: can we do more?

        shared.NETWORK_MANAGER.reset_package_registry()

    async def test_serialize_package_1(self):
        from mcpython import shared
        from mcpython.common.network.packages.DisconnectionPackage import (
            DisconnectionConfirmPackage,
        )
        from mcpython.engine.network.NetworkManager import load_packages
        from mcpython.engine.network.util import ReadBuffer

        await load_packages()

        package = DisconnectionConfirmPackage()
        data = await shared.NETWORK_MANAGER.encode_package(0, package)

        package2 = await shared.NETWORK_MANAGER.fetch_package_from_buffer(
            ReadBuffer(data)
        )

        self.assertIsInstance(package2, DisconnectionConfirmPackage)
        # todo: test more attributes

        shared.NETWORK_MANAGER.reset_package_registry()

    async def test_serialize_package_2(self):
        from mcpython import shared
        from mcpython.common.network.packages.HandShakePackage import (
            Client2ServerHandshake,
        )
        from mcpython.engine.network.NetworkManager import load_packages
        from mcpython.engine.network.util import ReadBuffer

        await load_packages()

        package = Client2ServerHandshake()
        package.previous_packages = [0, 45, 3234]
        data = await shared.NETWORK_MANAGER.encode_package(0, package)

        package2 = await shared.NETWORK_MANAGER.fetch_package_from_buffer(
            ReadBuffer(data)
        )

        self.assertIsInstance(package2, Client2ServerHandshake)
        self.assertEqual(package2.previous_packages, [0, 45, 3234])
        self.assertEqual(package2.package_id, 0)
        # todo: test more attributes

        shared.NETWORK_MANAGER.reset_package_registry()

    async def test_network_handler_fetch_1(self):
        from mcpython import shared
        from mcpython.engine.network.AbstractPackage import AbstractPackage

        class TestPackage(AbstractPackage):
            PACKAGE_NAME = "minecraft:test_package"
            PACKAGE_TYPE_ID = 1

            handled = False

            async def handle_inner(self):
                TestPackage.handled = True

        shared.NETWORK_MANAGER.reset_package_registry()
        shared.NETWORK_MANAGER.register_package_type(TestPackage)

        package = TestPackage()
        data = await shared.NETWORK_MANAGER.encode_package(0, package)
        self.assertNotEqual(len(data), 0)

        class stream:
            data_stream = bytearray(data)
            connected = True

            @classmethod
            def work(cls):
                pass

        shared.CLIENT_NETWORK_HANDLER = stream

        await shared.NETWORK_MANAGER.fetch_as_client()
        self.assertTrue(TestPackage.handled)
        self.assertEqual(len(stream.data_stream), 0)

        shared.NETWORK_MANAGER.reset_package_registry()
        shared.CLIENT_NETWORK_HANDLER = None

    async def test_network_handler_fetch_2(self):
        from mcpython import shared
        from mcpython.engine.network.AbstractPackage import AbstractPackage

        class TestPackage(AbstractPackage):
            PACKAGE_NAME = "minecraft:test_package"
            PACKAGE_TYPE_ID = 1

            handled = 0

            async def handle_inner(self):
                TestPackage.handled += 1

        shared.NETWORK_MANAGER.reset_package_registry()
        shared.NETWORK_MANAGER.register_package_type(TestPackage)

        package = TestPackage()
        data = await shared.NETWORK_MANAGER.encode_package(0, package)
        self.assertNotEqual(len(data), 0)

        class stream:
            data_stream = bytearray(data * 2)
            connected = True

            @classmethod
            def work(cls):
                pass

        shared.CLIENT_NETWORK_HANDLER = stream

        await shared.NETWORK_MANAGER.fetch_as_client()
        self.assertEqual(TestPackage.handled, 2)
        self.assertEqual(len(stream.data_stream), 0)

        shared.NETWORK_MANAGER.reset_package_registry()
        shared.CLIENT_NETWORK_HANDLER = None
