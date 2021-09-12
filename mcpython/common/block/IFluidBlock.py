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
from abc import ABC

import mcpython.common.block.AbstractBlock
import mcpython.common.fluid.AbstractFluid
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class IFluidBlock(mcpython.common.block.AbstractBlock.AbstractBlock, ABC):
    """
    Base class for fluid blocks

    Users need to simply extend this and set the UNDERLYING_FLUID property to their fluid instance

    todo: implement source / flow logic
    todo: implement renderer
    """

    # The underlying fluid, must be set for this to work
    UNDERLYING_FLUID: typing.Optional[
        mcpython.common.fluid.AbstractFluid.AbstractFluid
    ] = None

    def __init__(self):
        super().__init__()
        self.is_flowing = False
        self.flow_direction = 0, 0
        self.height = 0

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)
        buffer.write_bool(self.is_flowing)
        buffer.write_int(self.flow_direction[0])
        buffer.write_int(self.flow_direction[1])
        buffer.write_int(self.height)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)
        self.is_flowing = buffer.read_bool()
        self.flow_direction = buffer.read_int(), buffer.read_int()
        self.height = buffer.read_int()
