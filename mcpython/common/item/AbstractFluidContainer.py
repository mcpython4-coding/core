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

import mcpython.common.container.ResourceStack
import mcpython.common.item.AbstractItem


class AbstractArmorItem(mcpython.common.item.AbstractItem.AbstractItem, ABC):
    """
    Common base class for container-like items holding fluids
    """

    @classmethod
    def get_underlying_fluid_stacks(
        cls, itemstack: mcpython.common.container.ResourceStack.ItemStack
    ) -> typing.Iterable[mcpython.common.container.ResourceStack.FluidStack]:
        """
        Informal method for getting the fluids in the container [All of them]
        """
        return tuple()

    @classmethod
    def could_accept(
        cls,
        itemstack: mcpython.common.container.ResourceStack.ItemStack,
        fluidstack: mcpython.common.container.ResourceStack.FluidStack,
    ) -> bool:
        """
        Checks if the container could in theory accept the fluid given.
        When returning False, accept is never called
        """
        return False

    @classmethod
    def accept(
        cls,
        itemstack: mcpython.common.container.ResourceStack.ItemStack,
        fluidstack: mcpython.common.container.ResourceStack.FluidStack,
        insert_parts=True,
    ) -> bool:
        """
        Inserts a certain amount of fluid
        The fluidstack may contain remaining liquid if not everything could be accepted if insert_parts is True
        """

    @classmethod
    def can_provide(
        cls,
        itemstack: mcpython.common.container.ResourceStack.ItemStack,
        fluidstack: mcpython.common.container.ResourceStack.FluidStack,
    ) -> bool:
        """
        Checks if the given fluid container can provide the given fluid with the given amount
        """
        return False

    @classmethod
    def provide(
        cls,
        itemstack: mcpython.common.container.ResourceStack.ItemStack,
        fluidstack: mcpython.common.container.ResourceStack.FluidStack,
        extract_parts=True,
    ) -> bool:
        """
        Removes a certain amount of fluid from the container
        Is allowed to modify the fluidstack when not everything is provided when extract_parts is True
        """
