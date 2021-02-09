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
from abc import ABC

import pyglet

import mcpython.common.item.AbstractItem


class AbstractDamageBarItem(mcpython.common.item.AbstractItem.AbstractItem, ABC):
    def __init__(self):
        super().__init__()
        self.unbreakable = False

    def get_damage_info(
        self,
    ) -> typing.Optional[typing.Tuple[float, typing.Tuple[int, int, int]]]:
        raise NotImplementedError()


class DefaultDamageBarItem(AbstractDamageBarItem, ABC):
    def get_damage_info(
        self,
    ) -> typing.Optional[typing.Tuple[float, typing.Tuple[int, int, int]]]:
        damage = self.get_damage()
        if damage == 1 or self.unbreakable:
            return

        if damage > 0.5:
            return damage, (0, 255, 0)
        if damage > 0.25:
            return damage, (0, 128, 0)
        return damage, (255, 0, 0)

    def get_damage(self) -> float:
        raise NotImplementedError()


class DamageOnUseItem(DefaultDamageBarItem, ABC):
    DURABILITY: int = None

    def __init__(self):
        super().__init__()
        self.damage = self.DURABILITY

    def get_damage(self) -> float:
        return self.damage / self.DURABILITY

    def on_block_broken_with(self, itemstack, player, block):
        if player.gamemode in (0, 2):
            self.damage -= 1
        if self.damage <= 0:
            itemstack.clean()
