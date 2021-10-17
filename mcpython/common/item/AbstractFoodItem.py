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

import mcpython.common.item.AbstractItem
from mcpython import shared


class AbstractFoodItem(mcpython.common.item.AbstractItem.AbstractItem, ABC):
    HUNGER_ADDITION = None

    def on_eat(self, itemstack):
        """
        Called when the player eats the item
        :param itemstack: the itemstack to eat from
        :return: if the item was eaten or not
        """
        if shared.world.get_active_player().hunger == 20:
            return False
        shared.world.get_active_player().hunger = min(
            self.HUNGER_ADDITION + shared.world.get_active_player().hunger, 20
        )
        itemstack.add_amount(-1)
        return True

    def get_eat_hunger_addition(self) -> int:
        return self.HUNGER_ADDITION
