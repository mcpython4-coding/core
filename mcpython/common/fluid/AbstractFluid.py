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

import mcpython.common.event.api
import mcpython.engine.world.AbstractInterface
from mcpython import shared


class AbstractFluid(mcpython.common.event.api.IRegistryContent, ABC):
    """
    Abstract class defining fluid behaviour
    This is the stuff referenced by FluidStacks
    """

    TYPE = "minecraft:fluid"

    # The texture of the fluid, for rendering
    # Should be set to something meaningful for the fluid renderer
    TEXTURE_FLOW: str = "assets/missing_texture.png"
    TEXTURE_STILL: str = "assets/missing_texture.png"

    # Property of fluid blocks: are they creating infinite sources?
    IS_FINITE = False

    # Property of fluid blocks: are they creating a flow stream from the source?
    CREATE_FLOW_STREAM = True

    # Property of fluid block: is the source block moving along the flow?
    MOVE_SOURCE_BLOCK_ALONG_FLOW = False

    # Property for some mods; the temperature, in K
    DEFAULT_FLUID_TEMPERATURE: float = 303

    # The block name of the IFluidBlock for this fluid. If None, no fluid block is arrival
    FLUID_BLOCK_NAME: typing.Optional[str] = None

    # A FluidStack size which is "critical", that means that this class wants to be informed about it
    # Set to -1 if the smallest amount is critical
    CRITICAL_AMOUNT = -1

    # Set this to detect fluids touching with each other by the on_fluids_touching function
    # This can be used by e.g. lava for cobble gen
    CAN_BE_CRITICAL_ON_CONTACT = False

    # When the fluid solidifies, in K; Only for inter-mod information
    SOLIDIFICATION_POINT = -1

    # What does it solidify to?
    SOLIDIFIES_TO = "minecraft:air"

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.NAME is not None and cls.FLUID_BLOCK_NAME is None:
            import mcpython.common.block.BlockManager

            block_registry = shared.registry.get_by_name("minecraft:block")
            if block_registry.is_valid_key(cls.NAME):
                cls.FLUID_BLOCK_NAME = cls.NAME

    @classmethod
    def get_flow_rate_at(
        cls,
        dimension: mcpython.engine.world.AbstractInterface.IDimension,
        position: typing.Tuple[int, int, int],
    ) -> int:
        """
        How many ticks it take to flow one block further
        This function is only used when defining a FluidBlock with this fluid
        :param dimension: the dimension in
        :param position: the position at
        :return: the flow rate
        """
        return 10

    @classmethod
    def on_critical_amount_reached(cls, fluid_stack):
        """
        Called when a FluidStack of this item gets bigger than CRITICAL_AMOUNT
        todo: more meta information!
        :param fluid_stack: the fluid stack in
        """

    @classmethod
    def on_fluids_touching(
        cls,
        other: typing.Type["AbstractFluid"],
        dimension: mcpython.engine.world.AbstractInterface.IDimension,
        position_this: typing.Optional[typing.Tuple[float, float, float]],
        position_that: typing.Optional[typing.Tuple[float, float, float]],
        is_fluid_block=(True, True),
    ):
        """
        Called when this fluid is touching another one and CAN_BE_CRITICAL_ON_CONTACT is True

        :param other: the other fluid type
        :param dimension:the dimension in
        :param position_this: optional: were we are in the dimension
        :param position_that: optional: were the other fluid is in this dimension
        :param is_fluid_block: this and that are fluid blocks [the position is a pointer to a fluid block]?
        """
