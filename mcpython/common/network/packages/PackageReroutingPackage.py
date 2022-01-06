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
import typing

from mcpython import shared
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class PackageReroute(AbstractPackage):
    PACKAGE_NAME = "minecraft:package_routing"
    PACKAGE_TYPE_ID = 6

    def __init__(self):
        super().__init__()
        self.route_target: int = -1
        self.inner_package: typing.Optional[AbstractPackage] = None

    def set_package(self, target: int, package: AbstractPackage):
        self.route_target = target
        self.inner_package = package
        return self

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.route_target = buffer.read_int()
        self.inner_package = await shared.NETWORK_MANAGER.fetch_package_from_buffer(
            ReadBuffer(buffer.read_bytes(size_size=4))
        )

    async def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_int(self.route_target)
        buffer.write_bytes(
            await shared.NETWORK_MANAGER.encode_package(self.inner_package), size_size=4
        )

    async def handle_inner(self):
        # todo: can we prevent the encoding / decoding bit (we are routing, encoding should be equal)
        await shared.NETWORK_MANAGER.send_package(self.inner_package, self.route_target)
