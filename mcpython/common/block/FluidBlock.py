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
from mcpython import shared
from mcpython.client.rendering.blocks.FluidRenderer import FluidRenderer
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython.util.texture import hex_to_color
from pyglet.window import mouse


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

    FLUID_RENDERER = None

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0
    NO_ENTITY_COLLISION = True
    CUSTOM_WALING_SPEED_MULTIPLIER = 0.3

    IS_BREAKABLE = False

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if (
            cls.NAME is not None
            and cls.NAME != "minecraft:unknown_registry_content"
            and not shared.IS_TEST_ENV
            and shared.IS_CLIENT
        ):
            cls.FLUID_RENDERER = FluidRenderer(
                "{}:block/{}_still".format(*cls.NAME.split(":"))
            )

    def __init__(self):
        super().__init__()
        self.is_flowing = False
        self.flow_direction = 0, 0

        self.height = 7

    def on_block_added(self):
        if shared.IS_CLIENT:
            self.face_info.custom_renderer = self.FLUID_RENDERER

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


class WaterFluidBlock(IFluidBlock):
    NAME = "minecraft:water"
    UNDERLYING_FLUID = "minecraft:water"


if not shared.IS_TEST_ENV and shared.IS_CLIENT:
    # todo: make biome based
    WATER_COLOR = tuple(e / 255 for e in hex_to_color("3F76E4")) + (1,)
    WaterFluidBlock.FLUID_RENDERER.color = lambda *_: WATER_COLOR


class LavaFluidBlock(IFluidBlock):
    NAME = "minecraft:lava"
    UNDERLYING_FLUID = "minecraft:lava"
