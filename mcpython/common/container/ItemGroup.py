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


class ItemGroup:
    def __init__(self):
        self.entries: typing.List[ItemStack] = []
        self.has_lazy = False

    def add(self, entry: ItemStack):
        assert (
            isinstance(entry, LazyClassLoadItemstack) or not entry.is_empty()
        ), "itemstack cannot be empty!"
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
