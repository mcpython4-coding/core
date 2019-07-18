"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import pyglet
import gui.ItemStack
import item.ItemHandler
import texture.helpers
import ResourceLocator


SLOT_WIDTH = 10


class Slot:
    def __init__(self, itemstack=None, position=(0, 0)):
        self.itemstack = itemstack if itemstack else gui.ItemStack.ItemStack.get_empty()
        self.itemstack.item = G.itemhandler.items["minecraft:stone"]()
        self.itemstack.amount = 2
        self.position = position
        if self.itemstack.item:
            self.sprite: pyglet.sprite.Sprite = texture.helpers.to_pyglet_sprite(
                ResourceLocator.ResourceLocator(self.itemstack.item.get_item_image_location()).data)
        else:
            self.sprite = None
        self.amount_lable = pyglet.text.Label(text=self.itemstack.amount)
        self.__last_itemfile = self.itemstack.item.get_item_image_location() if self.itemstack.item else None

    def copy(self, position):
        return SlotCopy(position, self)

    def draw(self):
        if self.itemstack.item and self.itemstack.item.get_item_image_location() != self.__last_itemfile:
            self.sprite: pyglet.sprite.Sprite = texture.helpers.to_pyglet_sprite(
                ResourceLocator.ResourceLocator(self.itemstack.item.get_item_image_location()).data)
        elif not self.itemstack.item:
            self.sprite = None
        self.amount_lable.text = self.itemstack.amount
        if self.sprite:
            self.sprite.position = self.position
            self.sprite.draw()
            if self.itemstack.amount != 1:
                self.amount_lable.x, self.amount_lable.y = self.position[0] + SLOT_WIDTH + 2, self.position[0] - 2
                self.amount_lable.draw()
        self.__last_itemfile = self.itemstack.item.get_item_image_location() if self.itemstack.item else None


class SlotCopy:
    def __init__(self, position, master: Slot):
        self.master = master
        self.position = position

    def copy(self, position):
        return self.master.copy(position)

    def draw(self):
        if self.master.sprite:
            self.master.sprite.position = self.position
            self.master.sprite.draw()
            if self.master.itemstack.amount > 1:
                self.master.amount_lable.x = self.position[0] + SLOT_WIDTH + 2
                self.master.amount_lable.y = self.position[0] - 2
                self.master.amount_lable.draw()

