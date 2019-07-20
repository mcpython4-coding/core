"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import item.Item


class ItemStack:
    def __init__(self, item_name_or_instance, amount=1):
        if issubclass(type(item_name_or_instance), item.Item.Item):
            self.item = item
        elif item_name_or_instance in G.itemhandler.items:
            self.item = G.itemhandler.items[item_name_or_instance]()
        else:
            self.item = None
        self.amount = amount if self.item and 0 <= amount <= self.item.get_max_stack_size() else 0

    def copy(self):
        return ItemStack(self.item, self.amount)

    def clean(self):
        self.item = None
        self.amount = 0

    @staticmethod
    def get_empty():
        return ItemStack(None)

