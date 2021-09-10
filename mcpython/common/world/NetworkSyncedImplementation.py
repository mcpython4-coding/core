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
import os
import typing

import mcpython.common.world.AbstractInterface
import mcpython.util.math
from mcpython import shared

from .Dimension import Dimension
from .Chunk import Chunk


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
        """
        Used to get an chunk instance with an given position
        :param cx: the chunk x position or an tuple of (x, z)
        :param cz: the chunk z position or None íf cx is tuple
        :param generate: if the chunk should be scheduled for generation if it is not generated
        :param create: if the chunk instance should be created when it does not exist
        :return: the chunk instance or None
        """
        if cz is None:
            assert type(cx) == tuple
            cx, cz = cx

        # Is this chunk locally arrival?
        if (cx, cz) not in self.chunks:
            if not create:
                return

            self.chunks[(cx, cz)] = NetworkSyncedChunk(self, (cx, cz))

            from mcpython.common.network.packages.WorldDataExchangePackage import DataRequestPackage
            shared.NETWORK_MANAGER.send_package(DataRequestPackage().request_chunk(self.name, cx, cz))

        return self.chunks[(cx, cz)]


class NetworkSyncedChunk(Chunk):
    pass

