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
import itertools
import typing
from abc import ABC

from mcpython.common.container.ResourceStack import ItemStack
from mcpython.util.enums import EnumSide


class IBlockContainerExposer:
    """
    Interface for blocks for exposing an inventory this block exposes to the outside
    """

    async def get_all_inventories(self) -> list:
        return []

    async def get_inventories_for_side(self, side: EnumSide) -> list:
        return await self.get_all_inventories()

    async def get_slots_for_side(self, side: EnumSide) -> typing.Iterable:
        return itertools.chain(
            *(
                inventory.get_interaction_slots()
                for inventory in await self.get_inventories_for_side(side)
            )
        )

    async def get_underlying_item_stacks(
        self, side: EnumSide
    ) -> typing.Iterable[ItemStack]:
        """
        Informal method for getting the items in the container [All of them]
        """
        return tuple()

    async def could_accept_item(
        self,
        side: EnumSide,
        item: ItemStack,
    ) -> bool:
        """
        Checks if the container could in theory accept the item given.
        When returning False, accept is never called
        """
        return False

    async def accept_item(
        self,
        side: EnumSide,
        item: ItemStack,
        insert_parts=True,
    ) -> bool:
        """
        Inserts a certain amount of an item
        The itemstack may contain remaining items if not everything could be accepted if insert_parts is True
        """
        return False

    async def can_provide_item(
        self,
        side: EnumSide,
        item: ItemStack,
    ) -> bool:
        """
        Checks if the given item container can provide the given item with the given amount
        """
        return False

    async def provide_item(
        self,
        side: EnumSide,
        item: ItemStack,
        extract_parts=True,
    ) -> bool:
        """
        Removes a certain amount of the item from the container
        Is allowed to modify the itemstack when not everything is provided when extract_parts is True
        """


class SimpleInventoryWrappingContainer(IBlockContainerExposer, ABC):
    async def get_underlying_item_stacks(
        self, side: EnumSide
    ) -> typing.Iterable[ItemStack]:
        return itertools.chain(
            *(slot.get_itemstack() for slot in await self.get_slots_for_side(side))
        )

    async def could_accept_item(
        self,
        side: EnumSide,
        item: ItemStack,
    ) -> bool:
        working_stack = item.copy()
        for slot in await self.get_slots_for_side(side):
            if slot.is_item_allowed(working_stack) and (
                slot.get_itemstack().is_empty()
                or slot.get_itemstack().amount < slot.get_itemstack().item.STACK_SIZE
            ):
                delta = min(
                    slot.get_itemstack().item.STACK_SIZE - slot.get_itemstack().amount,
                    working_stack.amount,
                )
                working_stack.add_amount(-delta)
                if working_stack.amount <= 0:
                    return True

        return working_stack.amount <= 0

    async def accept_item(
        self,
        side: EnumSide,
        item: ItemStack,
        insert_parts=True,
    ) -> bool:
        working_stack = item.copy()
        for slot in await self.get_slots_for_side(side):
            if slot.is_item_allowed(working_stack) and (
                slot.get_itemstack().is_empty()
                or slot.get_itemstack().amount < slot.get_itemstack().item.STACK_SIZE
            ):
                delta = min(
                    slot.get_itemstack().item.STACK_SIZE - slot.get_itemstack().amount,
                    working_stack.amount,
                )
                working_stack.add_amount(-delta)
                slot.get_itemstack().add_amount(delta)
                await slot.call_update_async()
                if working_stack.amount <= 0:
                    return True

        return working_stack.amount <= 0

    async def can_provide_item(
        self,
        side: EnumSide,
        item: ItemStack,
    ) -> bool:
        working_stack = item.copy()
        for slot in await self.get_slots_for_side(side):
            if slot.get_itemstack().contains_same_resource(working_stack):
                delta = min(slot.get_itemstack().item.STACK_SIZE, working_stack.amount)
                working_stack.add_amount(-delta)
                if working_stack.amount <= 0:
                    return True

        return working_stack.amount <= 0

    async def provide_item(
        self,
        side: EnumSide,
        item: ItemStack,
        extract_parts=True,
    ) -> bool:
        working_stack = item.copy()
        for slot in await self.get_slots_for_side(side):
            if slot.get_itemstack().contains_same_resource(working_stack):
                delta = min(slot.get_itemstack().item.STACK_SIZE, working_stack.amount)
                working_stack.add_amount(-delta)
                slot.get_itemstack().add_amount(-delta)
                await slot.call_update_async()
                if working_stack.amount <= 0:
                    return True

        return working_stack.amount <= 0
