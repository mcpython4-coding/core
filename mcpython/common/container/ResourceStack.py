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
import copy
import typing
from abc import ABC

import mcpython.common.item.AbstractItem
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer


class AbstractResourceStack(IBufferSerializeAble, ABC):
    """
    Abstract class for stack like objects
    """

    @classmethod
    def create_empty(cls):
        raise NotImplementedError

    def copy(self) -> "AbstractResourceStack":
        raise NotImplementedError

    def copy_from(self, other: "AbstractResourceStack"):
        raise NotImplementedError

    def clean(self):
        raise NotImplementedError

    def is_empty(self) -> bool:
        raise NotImplementedError

    def contains_same_resource(self, other: "AbstractResourceStack") -> bool:
        raise NotImplementedError

    def has_more_than(self, other: "AbstractResourceStack") -> bool:
        raise NotImplementedError

    def get_difference(self, other: "AbstractResourceStack") -> "AbstractResourceStack":
        raise NotImplementedError

    def set_amount(self, amount) -> "AbstractResourceStack":
        raise NotImplementedError


class ItemStack(AbstractResourceStack):
    """
    Default implementation for item stacks
    """

    @classmethod
    def create_empty(cls):
        """
        Get an empty itemstack
        """
        return cls()

    def __init__(self, item_name_or_instance=None, amount=1, warn_if_unarrival=True):
        if isinstance(
            item_name_or_instance, mcpython.common.item.AbstractItem.AbstractItem
        ):
            self.item = item_name_or_instance

        elif isinstance(item_name_or_instance, str):
            if (
                item_name_or_instance
                in shared.registry.get_by_name("minecraft:item").full_entries
            ):
                self.item = shared.registry.get_by_name("minecraft:item").full_entries[
                    item_name_or_instance
                ]()
            else:
                if warn_if_unarrival:
                    logger.println(
                        "[FATAL] can't find item named '{}'".format(
                            item_name_or_instance
                        )
                    )
                self.item = None

        else:
            if item_name_or_instance is not None and warn_if_unarrival:
                logger.println(
                    "[FATAL] cannot create itemstack with unknown item type",
                    item_name_or_instance,
                )
            self.item = None

        self.amount = amount if self.item and 0 <= amount <= self.item.STACK_SIZE else 0
        self.nbt = {}

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_bool(self.is_empty())

        if not self.is_empty():
            buffer.write_int(self.amount)
            buffer.write_string(self.item.NAME)
            await self.item.write_to_network_buffer(buffer)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        if buffer.read_bool():
            self.clean()
        else:
            self.amount = buffer.read_int()
            item_name = buffer.read_string()
            try:
                self.item = shared.registry.get_by_name("minecraft:item").full_entries[
                    item_name
                ]()
            except KeyError:
                self.item = None
                self.amount = 0
            else:
                await self.item.read_from_network_buffer(buffer)

        return self

    def copy(self) -> "ItemStack":
        """
        Copies the itemstack
        :return: copy of this itemstack
        """
        instance = ItemStack(self.item, self.amount)
        if not self.is_empty():
            self.item.on_copy(self, instance)
        return instance

    def copy_from(self, other: "ItemStack"):
        self.item = other.item
        self.amount = other.amount
        if not self.is_empty():
            self.item.on_copy(other, self)

    def clean(self):
        """
        "Clean" the itemstack so that there is no data inside
        """
        if not self.is_empty():
            self.item.on_clean(self)
        self.item = None
        self.amount = 0

    def __eq__(self, other):
        if not type(other) == ItemStack:
            return False
        return self.item == other.item and self.amount == other.amount

    def is_empty(self) -> bool:
        return self.amount == 0 or self.item is None

    def get_item_name(self) -> typing.Optional[str]:
        return self.item.NAME if self.item else None

    def set_amount(self, amount: int) -> "ItemStack":
        self.amount = amount
        if self.amount <= 0:
            self.clean()
        return self

    def add_amount(self, amount: int, check_overflow=True) -> "ItemStack":
        self.set_amount(self.amount + amount)
        if self.amount <= 0:
            self.clean()
        if self.item and self.item.STACK_SIZE < self.amount and check_overflow:
            self.amount = self.item.STACK_SIZE
        return self

    def __str__(self) -> str:
        return "ItemStack(item='{}',amount='{}'{})".format(
            self.get_item_name(),
            self.amount,
            "" if self.is_empty() else ",data={}".format(self.item.get_data()),
        )

    def __repr__(self):
        return str(self)

    def contains_same_resource(self, other: "AbstractResourceStack") -> bool:
        return (
            isinstance(other, ItemStack)
            and self.get_item_name() == other.get_item_name()
        )

    def has_more_than(self, other: "AbstractResourceStack") -> bool:
        return self.contains_same_resource(other) and self.amount >= other.amount

    def get_difference(self, other: "AbstractResourceStack") -> "AbstractResourceStack":
        return (
            None
            if not self.contains_same_resource(other)
            else self.copy().set_amount(self.amount - other.amount)
        )


class LazyClassLoadItemstack(ItemStack):
    def __init__(self, item_name: str, amount=1):
        super().__init__(item_name, amount=amount, warn_if_unarrival=False)
        self.lazy_amount = amount
        self.lazy_item_name = item_name

    def lookup(self):
        self.copy_from(
            ItemStack(self.lazy_item_name, self.lazy_amount, warn_if_unarrival=False)
        )
        return self

    def __repr__(self):
        return f"LazyItemStack(current={super().__repr__()},linked='{self.lazy_item_name}')"


class FluidStack(AbstractResourceStack):
    @classmethod
    def create_empty(cls):
        return cls(None)

    def __init__(self, fluid: typing.Optional[str], amount: float = 0, nbt=None):
        self.fluid = fluid
        self.amount = amount
        self.nbt = {} if nbt is None else nbt

    def copy(self) -> "FluidStack":
        return FluidStack(self.fluid, self.amount, nbt=copy.deepcopy(self.nbt))

    def copy_from(self, other: "FluidStack"):
        self.fluid, self.amount = other.fluid, other.amount
        self.nbt = copy.deepcopy(other.nbt)
        return self

    def clean(self):
        self.fluid = None
        self.amount = 0
        self.nbt.clear()

    def is_empty(self) -> bool:
        return self.fluid is None or self.amount == 0

    def contains_same_resource(self, other: "FluidStack") -> bool:
        return (
            isinstance(other, FluidStack)
            and self.fluid == other.fluid
            and self.nbt == other.nbt
        )

    def has_more_than(self, other: "FluidStack") -> bool:
        return self.contains_same_resource(other) and self.amount >= other.amount

    def get_difference(self, other: "FluidStack") -> "FluidStack":
        return (
            None
            if not self.contains_same_resource(other)
            else self.copy().set_amount(self.amount - other.amount)
        )

    def set_amount(self, amount: float) -> "FluidStack":
        self.amount = amount
        return self

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_bool(self.is_empty())

        if not self.is_empty():
            buffer.write_float(self.amount)
            buffer.write_string(self.fluid)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        if not buffer.read_bool():
            self.clean()
        else:
            self.amount = buffer.read_float()
            self.fluid = buffer.read_string()
