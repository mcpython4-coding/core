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
import random
import typing
import uuid
from abc import ABC

from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer


class AbstractContainer(IBufferSerializeAble, ABC):
    """
    Base class for containers
    Can assign a certain ContainerRenderer to render stuff here
    """

    def __init__(self):
        self.slots = []
        self.custom_name = ""
        self.uuid = uuid.uuid4()

        shared.inventory_handler.add(self)

        self.create_slots()
        for slot in self.slots:
            slot.assigned_inventory = self

        if not shared.IS_CLIENT:
            self.renderer = None
        else:
            self.renderer = self.create_renderer()
            self.renderer.create_slot_rendering_information()

    def create_slots(self):
        """
        Invoked during construction of the object; should fill the slots array with slot instances
        """

    def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.custom_name)
        buffer.write_uuid(self.uuid)

        buffer.write_int(len(self.slots))

        for slot in self.slots:
            slot.write_to_network_buffer(buffer)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        self.custom_name = buffer.read_string()
        self.uuid = buffer.read_uuid()

        if buffer.read_int() != len(self.slots):
            logger.println(f"[SERIALIZER][WARN] Server and client don't agree on the slot count of inventory {self}, skipping slot deserializer...")
            return

        for slot in self.slots:
            slot.read_from_network_buffer(buffer)

    def create_renderer(self) -> typing.Any:
        """
        Called when loading a client to create the renderer; this is the only part which should interact
        with client-only code in this class
        :return: A ContainerRenderer instance
        """

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
        if self in shared.inventory_handler.open_containers:
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
        Called when the inventory should update the content of the ShiftContainer of the inventory-handler
        """
