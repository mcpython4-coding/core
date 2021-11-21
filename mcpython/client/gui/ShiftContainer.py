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
from mcpython.common.container.ResourceStack import ItemStack


class ShiftContainer:
    """
    Container class holding information on which inventory parts can be shift-clicked
    todo: is their no better way of doing this?
    todo: maybe add more than two sides?
    """

    def __init__(self):
        self.container_A = list()
        self.container_B = list()

    def get_opposite_item_list_for(self, slot):
        if slot in self.container_A:
            return self.container_B

        if slot in self.container_B:
            return self.container_A

        return []

    def move_to_opposite(self, slot, count=None) -> bool:
        if slot.itemstack.is_empty():
            return True

        if count is not None and slot.itemstack.amount < count:
            count = slot.itemstack.amount

        opposite = self.get_opposite_item_list_for(slot)
        itemstack_to_move = slot.get_linked_itemstack_for_sift_clicking()

        if len(opposite) == 0:
            return False

        for slot2 in opposite:
            if (
                slot2.itemstack.item == itemstack_to_move.item
                and slot.interaction_mode[1]
            ):
                delta = min(
                    itemstack_to_move.amount if count is None else count,
                    slot2.itemstack.item.STACK_SIZE - slot2.itemstack.amount,
                )
                slot2.get_itemstack().add_amount(delta)
                itemstack_to_move.add_amount(-delta)

                slot2.call_update(True)
                slot.call_update(True)

                if itemstack_to_move.is_empty() or count is not None:
                    return True

        for slot2 in opposite:
            if slot2.get_itemstack().is_empty() and slot.interaction_mode[1]:
                if count is None:
                    slot2.set_itemstack(itemstack_to_move.copy())
                    slot.set_itemstack(ItemStack.create_empty())
                    slot.call_update(True)
                else:
                    slot2.set_itemstack(itemstack_to_move.copy().set_amount(count))
                    itemstack_to_move.add_amount(-count)
                    slot.call_update(True)
                return True

        return False
