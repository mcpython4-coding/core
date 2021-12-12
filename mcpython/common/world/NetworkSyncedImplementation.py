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

from .Chunk import Chunk
from .Dimension import Dimension


class NetworkSyncedDimension(Dimension):
    """
    Class holding a whole dimension on a client connected to a dedicated server
    """

    def get_chunk(
        self,
        cx: typing.Union[int, typing.Tuple[int, int]],
        cz: int = None,
        generate: bool = True,
        create: bool = True,
    ) -> typing.Optional["NetworkSyncedChunk"]:
        if cz is None:
            if type(cx) != tuple:
                raise ValueError

            cx, cz = cx

        # Is this chunk locally arrival?
        if (cx, cz) not in self.chunks:
            if not create:
                return

            print(cx, cz, self.name, self)

            self.chunks[(cx, cz)] = NetworkSyncedChunk(self, (cx, cz))

            from mcpython.common.network.packages.WorldDataExchangePackage import (
                DataRequestPackage,
            )

            shared.tick_handler.schedule_once(
                shared.NETWORK_MANAGER.send_package(
                    DataRequestPackage().request_chunk(self.name, cx, cz)
                )
            )

        return self.chunks[(cx, cz)]


class NetworkSyncedChunk(Chunk):
    async def add_block(
        self,
        *args,
        network_sync=True,
        **kwargs,
    ):
        b = await super().add_block(*args, **kwargs, network_sync=False)

        if network_sync:
            from mcpython.common.network.packages.WorldDataExchangePackage import (
                ChunkBlockChangePackage,
            )

            await shared.NETWORK_MANAGER.send_package_to_all(
                ChunkBlockChangePackage()
                .set_dimension(self.dimension.get_name())
                .change_position(b.position, b),
                not_including=shared.NETWORK_MANAGER.client_id,
            )

        return b

    async def remove_block(self, *args, network_sync=True, **kwargs):
        await super().remove_block(*args, network_sync=False, **kwargs)

        if network_sync:
            from mcpython.common.network.packages.WorldDataExchangePackage import (
                ChunkBlockChangePackage,
            )

            await shared.NETWORK_MANAGER.send_package_to_all(
                ChunkBlockChangePackage()
                .set_dimension(self.dimension.get_name())
                .change_position(args[0], None),
                not_including=shared.NETWORK_MANAGER.client_id,
            )
