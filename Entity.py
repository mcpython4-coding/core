"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import gui.ItemStack


class Entity:
    """
    dummy class for every entity
    """

    def __init__(self):
        self.position = (0, 0, 0)
        self.rotation = (0, 0)
        self.inventory_slots = []
        self.harts = 0

    def tell(self, msg: str): pass

    def kill(self): pass

    def add_to_free_place(self, itemstack: gui.ItemStack.ItemStack) -> bool: pass

    def damage(self, damage): pass

