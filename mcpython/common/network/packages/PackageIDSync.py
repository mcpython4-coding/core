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
from mcpython import shared
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class PackageIDSync(AbstractPackage):
    """
    Package client -> server for syncing up package id's
    """

    PACKAGE_TYPE_ID = 5
    PACKAGE_NAME = "minecraft:package_id_sync"

    def __init__(self):
        super().__init__()
        self.data = []

    def setup(self):
        self.data = shared.NETWORK_MANAGER.get_dynamic_id_info()
        return self

    async def write_to_buffer(self, buffer: WriteBuffer):
        await buffer.write_list(
            self.data, lambda e: buffer.write_string(e[0]).write_int(e[1])
        )

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.data = [e async for e in buffer.read_list(lambda: (buffer.read_string(), buffer.read_int()))]

    async def handle_inner(self):
        await shared.NETWORK_MANAGER.set_dynamic_id_info(self.data)
