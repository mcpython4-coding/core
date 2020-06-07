"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.item.Item


class ItemFood(mcpython.item.Item.Item):
    def on_eat(self):
        """
        called when the player eats the item
        :return: if the item was eaten or not
        """
        if G.world.get_active_player().hunger == 20:
            return False
        G.world.get_active_player().hunger = min(self.HUNGER_ADDITION+G.world.get_active_player().hunger, 20)
        return True

    HUNGER_ADDITION = None

    def get_eat_hunger_addition(self) -> int:
        return self.HUNGER_ADDITION
