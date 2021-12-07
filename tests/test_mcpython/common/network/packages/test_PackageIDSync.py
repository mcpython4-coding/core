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


class TestPackageIDSync(TestCase):
    def test_module_import(self):
        import mcpython.common.network.packages.PackageIDSync

    async def test_setup(self):
        import mcpython.engine.network.NetworkManager
        from mcpython import shared
        from mcpython.common.network.packages.PackageIDSync import PackageIDSync

        await mcpython.engine.network.NetworkManager.load_packages()

        package = PackageIDSync()
        package.setup()

        self.assertEqual(
            list(sorted(package.data, key=lambda e: e[0])),
            list(
                sorted(shared.NETWORK_MANAGER.get_dynamic_id_info(), key=lambda e: e[0])
            ),
        )

        shared.NETWORK_MANAGER.reset_package_registry()

    async def test_serialize(self):
        import mcpython.engine.network.NetworkManager
        from mcpython import shared
        from mcpython.common.network.packages.PackageIDSync import PackageIDSync
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        await mcpython.engine.network.NetworkManager.load_packages()

        package = PackageIDSync()
        package.setup()

        buffer = WriteBuffer()
        package.write_to_buffer(buffer)

        shared.NETWORK_MANAGER.reset_package_registry()

        package2 = PackageIDSync()
        package2.read_from_buffer(ReadBuffer(buffer.get_data()))

        self.assertEqual(package.data, package2.data)

        shared.NETWORK_MANAGER.reset_package_registry()

    async def test_handle_inner(self):
        import mcpython.engine.network.NetworkManager
        from mcpython import shared
        from mcpython.common.network.packages.PackageIDSync import PackageIDSync
        from mcpython.engine.network.util import ReadBuffer, WriteBuffer

        await mcpython.engine.network.NetworkManager.load_packages()

        package = PackageIDSync()
        package.setup()

        buffer = WriteBuffer()
        package.write_to_buffer(buffer)

        previous_data = shared.NETWORK_MANAGER.get_dynamic_id_info()

        await package.handle_inner()

        self.assertEqual(
            list(sorted(previous_data, key=lambda e: e[0])),
            list(
                sorted(shared.NETWORK_MANAGER.get_dynamic_id_info(), key=lambda e: e[0])
            ),
        )

        shared.NETWORK_MANAGER.reset_package_registry()
