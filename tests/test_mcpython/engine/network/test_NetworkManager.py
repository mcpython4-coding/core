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

    async def test_dynamic_id_info(self):
        from mcpython import shared
        from mcpython.engine.network.NetworkManager import load_packages

        await load_packages()

        data = shared.NETWORK_MANAGER.get_dynamic_id_info()

        await shared.NETWORK_MANAGER.set_dynamic_id_info(data)

        self.assertNotEqual(len(shared.NETWORK_MANAGER.package_types), 0)

        # todo: can we do more?

        shared.NETWORK_MANAGER.reset_package_registry()

    async def test_serialize_package(self):
        from mcpython import shared
        from mcpython.common.network.packages.DisconnectionPackage import (
            DisconnectionConfirmPackage,
        )
        from mcpython.engine.network.NetworkManager import load_packages

        await load_packages()

        package = DisconnectionConfirmPackage()
        data = await shared.NETWORK_MANAGER.encode_package(0, package)

        package2 = await shared.NETWORK_MANAGER.fetch_package_from_buffer(
            bytearray(data)
        )

        self.assertIsInstance(package2, DisconnectionConfirmPackage)
        # todo: test more attributes

        shared.NETWORK_MANAGER.reset_package_registry()
