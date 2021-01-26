"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from abc import ABC

from mcpython import shared
import random


class AbstractContainer(ABC):
    """
    Base class for containers
    Currently, unused
    Later planned to be part of the inventory system; the shared part [the inventory is client-only]
    Currently, the API is only a copy of Inventory parts for shared
    todo: do more here!
    """

    @classmethod
    def create_renderer(cls):
        """
        Called when loading a client to create the renderer; this is the only part which should interact
        with client-only code in this class
        """

    def __init__(self):
        self.slots = []

    def tick(self, dt: float):
        pass

    def is_closable_by_escape(self) -> bool:
        return True

    def is_always_open(self) -> bool:
        return False

    def is_blocking_interactions(self) -> bool:
        return True

    def on_world_cleared(self):
        [slot.get_itemstack().clean() for slot in self.slots]
        if self in shared.inventory_handler.opened_inventory_stack:
            shared.inventory_handler.hide(self)

    def get_interaction_slots(self):
        return self.slots

    def clear(self):
        for slot in self.slots:
            slot.get_itemstack().clean()

    def copy(self):
        obj = self.__class__()
        for i in range(3 * 9):
            obj.slots[i].set_itemstack(self.slots[i].get_itemstack().copy())
        return obj

    def load(self, data) -> bool:
        """
        serializes the data into the inventory
        :param data: the data saved
        :return: if load is valid or not
        """
        return True

    def post_load(self, data):
        """
        serializes stuff after the the slot data is loaded
        :param data: the data stored
        """

    def save(self):
        """
        serializes the inventory into an pickle-able data stream
        :return: the data
        """
        return "no:data"

    def insert_items(
        self, items: list, random_check_order=False, insert_when_same_item=True
    ) -> list:
        skipped = []
        while len(items) > 0:
            stack = items.pop(0)
            if not self.insert_item(
                stack,
                random_check_order=random_check_order,
                insert_when_same_item=insert_when_same_item,
            ):
                skipped.append(stack)
        return skipped

    def insert_item(
        self, itemstack, random_check_order=False, insert_when_same_item=True
    ) -> bool:
        if itemstack.is_empty():
            return True
        slots = self.slots.copy()
        if random_check_order:
            random.shuffle(slots)
        for slot in slots:
            if slot.itemstack.is_empty():
                slot.set_itemstack(itemstack)
                return True
            elif slot.itemstack.get_item_name() == itemstack.get_item_name():
                if (
                    slot.itemstack.amount + itemstack.amount
                    <= itemstack.item.STACK_SIZE
                ):
                    slot.itemstack.add_amount(itemstack.amount)
                    return True
                elif insert_when_same_item:
                    overflow = itemstack.amount - (
                        itemstack.item.STACK_SIZE - slot.itemstack.amount
                    )
                    slot.itemstack.amount = itemstack.item.STACK_SIZE
                    itemstack.set_amount(overflow)
        # logger.println("itemstack overflow: ".format(itemstack))
        return False

    def update_shift_container(self):
        """
        called when the inventory should update the content of the ShiftContainer of the inventory-handler
        """
