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
import re
import typing

from mcpython.common.container.ResourceStack import ItemStack, LazyClassLoadItemstack
from mcpython.engine.network.util import IBufferSerializeAble, WriteBuffer, ReadBuffer


class ItemGroup(IBufferSerializeAble):
    def __init__(self):
        self.entries: typing.List[ItemStack] = []
        self.has_lazy = False

    def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_list(self.entries, lambda e: e.write_to_network_buffer(buffer))

    def read_from_network_buffer(self, buffer: ReadBuffer):
        self.entries = buffer.read_list(lambda: ItemStack().read_from_network_buffer(buffer))

    def add(self, entry: typing.Union[ItemStack, str]):
        if isinstance(entry, str):
            entry = ItemStack(entry)

        if isinstance(entry, LazyClassLoadItemstack) or not entry.is_empty():
            raise ValueError(f"Itemstack {entry} cannot be empty or lazy!")

        self.entries.append(entry.set_amount(1))

        if isinstance(entry, LazyClassLoadItemstack):
            self.has_lazy = True

        return self

    def load_lazy(self):
        if not self.has_lazy:
            return

        has = False
        for entry in self.entries:
            if isinstance(entry, LazyClassLoadItemstack):
                entry.lookup()

                if entry.is_empty():
                    has = True

        self.has_lazy = has

    def sort_after_item_name(self):
        self.entries.sort(key=lambda stack: stack.get_item_name())
        return self

    def view(self) -> typing.Iterator[ItemStack]:
        return self.entries

    def filter_for(self, pattern: re.Pattern) -> typing.Iterator[ItemStack]:
        for entry in self.entries:
            if entry.is_empty():
                continue

            if pattern.fullmatch(entry.get_item_name()):
                yield entry

    def filtered(self):
        instance = FilteredItemGroup()
        instance.entries = self.entries
        return instance


class FilteredItemGroup(ItemGroup):
    def __init__(self):
        super().__init__()
        self.raw_filter: str = None
        self.filter: re.Pattern = None

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)
        buffer.write_string(self.raw_filter)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)
        self.apply_filter(buffer.read_string())

    def view(self) -> typing.Iterator[ItemStack]:
        return self.filter_for(self.filter)

    def apply_raw_filter(self, filter: str):
        self.raw_filter = filter
        self.filter = re.compile(filter)
        return self

    def apply_filter(self, filter: re.Pattern):
        self.raw_filter = None
        self.filter = filter
        return self
