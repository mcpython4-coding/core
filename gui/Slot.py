"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import pyglet
import gui.ItemStack
import item.ItemHandler
import texture.helpers
import ResourceLocator


SLOT_WIDTH = 32


class Slot:
    def __init__(self, itemstack=None, position=(0, 0), allow_player_remove=True, allow_player_insert=True,
                 allow_player_add_to_free_place=True):
        self.itemstack = itemstack if itemstack else gui.ItemStack.ItemStack.get_empty()
        # self.itemstack.item = G.itemhandler.items["minecraft:stone"]()
        # self.itemstack.amount = 2
        self.position = position
        if self.itemstack.item:
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(G.itemhandler.pygletimagetable[
                                                                         self.itemstack.item.get_name()])
        else:
            self.sprite = None
        self.amount_lable = pyglet.text.Label(text=str(self.itemstack.amount))
        self.__last_itemfile = self.itemstack.item.get_item_image_location() if self.itemstack.item else None
        self.interaction_mode = [allow_player_remove, allow_player_insert, allow_player_add_to_free_place]

    def copy(self, position=(0, 0)):
        return SlotCopy(position, self)

    def draw(self, dx, dy):
        if self.itemstack.item and self.itemstack.item.get_item_image_location() != self.__last_itemfile:
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(G.itemhandler.pygletimagetable[
                                                                         self.itemstack.item.get_name()])
        elif not self.itemstack.item:
            self.sprite = None
        self.amount_lable.text = str(self.itemstack.amount)
        if self.sprite:
            self.sprite.position = (self.position[0] + dx, self.position[1] + dy)
            self.sprite.draw()
            if self.itemstack.amount != 1:
                self.amount_lable.x = self.position[0] + SLOT_WIDTH + 2 + dx
                self.amount_lable.y = self.position[1] - 2 + dy
                self.amount_lable.draw()
        self.__last_itemfile = self.itemstack.item.get_item_image_location() if self.itemstack.item else None

    def draw_lable(self):
        """
        these code draws only the lable, before, normal draw must be executed
        """
        if self.itemstack.amount > 1:
            self.amount_lable.draw()


class SlotCopy:
    def __init__(self, position, master: Slot, allow_player_remove=True, allow_player_insert=True,
                 allow_player_add_to_free_place=True):
        self.master = master
        self.position = position
        self.interaction_mode = [allow_player_remove, allow_player_insert, allow_player_add_to_free_place]

    def set_itemstack(self, itemstack: gui.ItemStack.ItemStack):
        self.master.itemstack = itemstack

    def get_itemstack(self) -> gui.ItemStack.ItemStack:
        return self.master.itemstack

    itemstack = property(get_itemstack, set_itemstack)

    def copy(self, position=(0, 0)):
        return self.master.copy(position)

    def draw(self, dx, dy):
        if self.master.sprite:
            self.master.sprite.position = (self.position[0] + dx, self.position[1] + dy)
            self.master.sprite.draw()
            if self.master.itemstack.amount > 1:
                self.master.amount_lable.x = self.position[0] + SLOT_WIDTH + 2 + dx
                self.master.amount_lable.y = self.position[1] - 2 + dy

    def draw_lable(self):
        """
        these code draws only the lable, before, normal draw must be executed
        """
        if self.master.itemstack.amount > 1:
            self.master.amount_lable.draw()

