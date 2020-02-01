"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import item.Item


class ItemFood(item.Item.Item):
    def on_eat(self):
        """
        called when the player eats the item
        :return: if the item was eaten or not
        """
        if G.player.hunger == 20:
            return False
        G.player.hunger = min(self.get_eat_hunger_addition()+G.player.hunger, 20)
        return True

    def get_eat_hunger_addition(self) -> int:
        raise NotImplementedError()

