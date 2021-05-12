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

from mcpython.common.container.ResourceStack import ItemStack


class ItemGroup:
    def __init__(self):
        self.entries: typing.List[ItemStack] = []

    def add(self, entry: ItemStack):
        assert not entry.is_empty(), "itemstack cannot be empty!"
        self.entries.append(entry.set_amount(1))
        return self

    def sort_after_item_name(self):
        self.entries.sort(key=lambda stack: stack.get_item_name())
        return self
