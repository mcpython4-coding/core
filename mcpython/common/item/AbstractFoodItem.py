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
import mcpython.common.item.AbstractItem


class AbstractFoodItem(mcpython.common.item.AbstractItem.AbstractItem, ABC):
    HUNGER_ADDITION = None

    def on_eat(self):
        """
        called when the player eats the item
        :return: if the item was eaten or not
        """
        if shared.world.get_active_player().hunger == 20:
            return False
        shared.world.get_active_player().hunger = min(
            self.HUNGER_ADDITION + shared.world.get_active_player().hunger, 20
        )
        return True

    def get_eat_hunger_addition(self) -> int:
        return self.HUNGER_ADDITION
