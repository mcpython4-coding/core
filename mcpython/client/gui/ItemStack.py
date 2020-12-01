"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals as G, logger
import mcpython.common.item.Item


class ItemStack:
    """
    base class for item stored somewhere
    todo: add function to copy content from one ItemStack to another
    """

    def __init__(self, item_name_or_instance, amount=1):
        if issubclass(type(item_name_or_instance), mcpython.common.item.Item.Item):
            self.item = item_name_or_instance
        elif type(item_name_or_instance) == str:
            if (
                item_name_or_instance
                in G.registry.get_by_name("item").registered_object_map
            ):
                self.item = G.registry.get_by_name("item").registered_object_map[
                    item_name_or_instance
                ]()
            else:
                logger.println(
                    "[FATAL] can't find item named '{}'".format(item_name_or_instance)
                )
                self.item = None
        else:
            self.item = None
        self.amount = amount if self.item and 0 <= amount <= self.item.STACK_SIZE else 0

    def copy(self):
        """
        copy the itemstack
        :return: copy of itself
        """
        # todo: copy item data
        return ItemStack(self.item, self.amount)

    def clean(self):
        """
        clean the itemstack
        """
        self.item = None
        self.amount = 0

    @staticmethod
    def get_empty():
        """
        get an empty itemstack
        """
        return ItemStack(None)

    def __eq__(self, other):
        if not type(other) == ItemStack:
            return False
        return self.item == other.item and self.amount == other.amount

    def is_empty(self):
        return self.amount == 0 or self.item is None

    def get_item_name(self):
        return self.item.NAME if self.item else None

    def set_amount(self, amount):
        self.amount = amount
        if self.amount <= 0:
            self.clean()
        return self

    def add_amount(self, amount, check_overflow=True):
        self.set_amount(self.amount + amount)
        if self.amount <= 0:
            self.clean()
        if self.item and self.item.STACK_SIZE < self.amount and check_overflow:
            self.amount = self.item.STACK_SIZE
        return self

    def __str__(self):
        # todo: include item data
        return "ItemStack(item='{}',amount='{}'{})".format(
            self.get_item_name(),
            self.amount,
            "" if self.is_empty() else ",data={}".format(self.item.get_data()),
        )
