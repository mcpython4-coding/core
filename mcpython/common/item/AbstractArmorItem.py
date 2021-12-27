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
from abc import ABC

import mcpython.common.item.AbstractDamageBarItem
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class AbstractArmorItem(
    mcpython.common.item.AbstractDamageBarItem.DefaultDamageBarItem, ABC
):
    DURABILITY = 0

    def __init__(self):
        super().__init__()
        self.damage = self.DURABILITY

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)
        buffer.write_int(self.damage)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)
        self.damage = buffer.read_int()

    DEFENSE_POINTS = 0

    async def get_defense_points(self):
        return self.DEFENSE_POINTS

    STACK_SIZE = 1

    def get_damage(self, itemstack) -> float:
        return self.damage / self.DURABILITY

    def get_data(self):
        return self.damage

    def set_data(self, data):
        try:
            self.damage = int(data)
        except ValueError:
            pass
