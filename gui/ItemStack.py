"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import item.Item


class ItemStack:
    """
    base class for item stored somewhere
    """
    
    def __init__(self, item_name_or_instance, amount=1):
        if issubclass(type(item_name_or_instance), item.Item.Item):
            self.item = item_name_or_instance
        elif item_name_or_instance in G.registry.get_by_name("item").get_attribute("items"):
            self.item = G.registry.get_by_name("item").get_attribute("items")[item_name_or_instance]()
        else:
            self.item = None
        self.amount = amount if self.item and 0 <= amount <= self.item.get_max_stack_size() else 0

    def copy(self):
        """
        copy the itemstack
        :return: copy of itself
        """
        return ItemStack(self.item, self.amount)

    def clean(self):
        """
        clean the itemstack
        """
        self.item = None
        self.amount = 0

    @staticmethod
    def get_empty():
        """
        get an empty itemstack
        """
        return ItemStack(None)

    def __eq__(self, other):
        if not type(other) == ItemStack: return False
        return self.item == other.item and self.amount == other.amount

