"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""


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

        if len(opposite) == 0:
            return False

        for slot2 in opposite:
            if slot2.itemstack.item == slot.itemstack.item and slot.interaction_mode[1]:
                delta = min(
                    slot.itemstack.amount if count is None else count,
                    slot2.itemstack.item.STACK_SIZE - slot2.itemstack.amount,
                )
                slot2.itemstack.add_amount(delta)
                slot.itemstack.add_amount(-delta)
                if slot.itemstack.is_empty() or count is not None:
                    return True

        for slot2 in opposite:
            if slot2.itemstack.is_empty() and slot.interaction_mode[1]:
                if count is None:
                    slot2.set_itemstack(slot.itemstack.copy())
                    slot.itemstack.clean()
                else:
                    slot2.set_itemstack(slot.itemstack.copy().set_amount(count))
                    slot.itemstack.add_amount(-count)
                return True

        return False
