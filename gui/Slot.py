"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import pyglet
import gui.ItemStack
import item.ItemHandler
# import texture.helpers
import ResourceLocator
import traceback
import logger


SLOT_WIDTH = 32

PYGLET_IMAGE_HOVERING = pyglet.sprite.Sprite(
    ResourceLocator.read("assets/minecraft/textures/gui/hotbar_selected.png", "pyglet"))


class Slot:
    """
    slot class
    """

    def __init__(self, itemstack=None, position=(0, 0), allow_player_remove=True, allow_player_insert=True,
                 allow_player_add_to_free_place=True, on_update=None, allow_half_getting=True, on_shift_click=None,
                 empty_image=None, allowed_item_tags=None, allowed_item_test=None):
        """
        creates an new slot
        :param itemstack: the itemstack to use
        :param position: the position to create at
        :param allow_player_remove: if the player is allowed to remove items out of it
        :param allow_player_insert: if the player is allowed to insert items into it
        :param allow_player_add_to_free_place: if items can be added direct to system
        :param on_update: called when the slot is updated
        :param allow_half_getting: can the player get only the half of the items out of the slot?
        :param on_shift_click: called when shift-clicked on the block
        """
        self.__itemstack = itemstack if itemstack else gui.ItemStack.ItemStack.get_empty()
        # self.itemstack.item = G.itemhandler.items["minecraft:stone"]()
        # self.itemstack.amount = 2
        self.position = position
        if self.__itemstack.item:
            pos, index = item.ItemHandler.items.get_attribute("itemindextable")[self.__itemstack.item.get_name()][
                self.__itemstack.item.get_active_image_location()]
            image = item.ItemHandler.TEXTURE_ATLASES[index].group[tuple(pos)]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        else:
            self.sprite = None
        self.amount_label = pyglet.text.Label(text=str(self.__itemstack.amount), anchor_x="right")
        self.__last_itemfile = self.__itemstack.item.get_default_item_image_location() if self.__itemstack.item else None
        self.interaction_mode = [allow_player_remove, allow_player_insert, allow_player_add_to_free_place]
        self.on_update = [on_update] if on_update else []
        self.allow_half_getting = allow_half_getting
        self.on_shift_click = on_shift_click
        self.amount_label = pyglet.text.Label()
        self.childs = []
        self.empty_image = pyglet.sprite.Sprite(empty_image) if empty_image else None
        self.allowed_item_tags = allowed_item_tags
        self.allowed_item_func = allowed_item_test

    def get_itemstack(self):
        return self.__itemstack

    def set_itemstack(self, stack, update=True, player=False):
        self.__itemstack = stack if stack else gui.ItemStack.ItemStack.get_empty()
        if update:
            self.call_update(player=player)

    def call_update(self, player=False):
        if not self.on_update: return
        [f(player=player) for f in self.on_update]

    itemstack = property(get_itemstack, set_itemstack)

    def copy(self, position=(0, 0)):
        """
        creates an copy of self
        :param position: the position to create at
        :return: a slotcopy pointing to this
        """
        return SlotCopy(self, position=position)

    def draw(self, dx=0, dy=0, hovering=False):
        """
        draws the slot
        """
        if hovering:
            PYGLET_IMAGE_HOVERING.position = (self.position[0] + dx, self.position[1] + dy)
            PYGLET_IMAGE_HOVERING.draw()
        if self.__itemstack.item and self.__itemstack.item.get_default_item_image_location() != self.__last_itemfile:
            pos, index = item.ItemHandler.items.get_attribute("itemindextable")[self.__itemstack.item.get_name()][
                self.__itemstack.item.get_active_image_location()]
            image = item.ItemHandler.TEXTURE_ATLASES[index].group[tuple(pos)]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
            self.__last_itemfile = self.__itemstack.item.get_default_item_image_location() if self.__itemstack.item \
                else None
        elif not self.__itemstack.item:
            self.sprite = None
            if self.empty_image:
                self.empty_image.position = (self.position[0] + dx, self.position[1] + dy)
                self.empty_image.draw()
        self.amount_label.text = str(self.__itemstack.amount)
        if self.sprite:
            self.sprite.position = (self.position[0] + dx, self.position[1] + dy)
            self.sprite.draw()
            if self.__itemstack.amount != 1:
                self.amount_label.x = self.position[0] + SLOT_WIDTH + dx
                self.amount_label.y = self.position[1] - dy
                self.amount_label.draw()

    def draw_lable(self, x, y):
        """
        these code draws only the lable, before, normal draw should be executed for correcrt setup
        """
        if self.__itemstack.amount > 1:
            self.amount_label.text = str(self.__itemstack.amount)
            self.amount_label.x = self.position[0] + SLOT_WIDTH + x
            self.amount_label.y = self.position[1] - y
            self.amount_label.draw()

    def can_set_item(self, itemstack) -> bool:
        itemname = itemstack.get_item_name()
        flag1 = self.allowed_item_tags is not None
        flag2 = flag1 and (any([itemname in G.taghandler.taggroups["items"].tags[x].entries for x in
                                self.allowed_item_tags]) or itemstack.get_item_name() is None)
        flag3 = self.allowed_item_func is not None
        flag4 = flag3 and self.allowed_item_func(itemstack)
        try:
            return (flag1 and flag2) or (flag3 and flag4) or not (flag1 or flag3)
        except:
            logger.println("[GUI][ERROR] error during executing check func '{}'".format(self.allowed_item_func))
            traceback.print_exc()
            return False


class SlotCopy:
    def __init__(self, master, position=(0, 0), allow_player_remove=True, allow_player_insert=True,
                 allow_player_add_to_free_place=True, on_update=None, allow_half_getting=True, on_shift_click=None):
        self.master: Slot = master
        self.position = position
        if self.get_itemstack().item:
            pos, index = item.ItemHandler.items.get_attribute("itemindextable")[self.get_itemstack().item.get_name()][
                self.get_itemstack().item.get_active_image_location()]
            image = item.ItemHandler.TEXTURE_ATLASES[index].group[tuple(pos)]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        else:
            self.sprite = None
        self.__last_itemfile = self.itemstack.item.get_default_item_image_location() if self.itemstack.item else None
        self.interaction_mode = [allow_player_remove, allow_player_insert, allow_player_add_to_free_place]
        self.on_update = [on_update] if on_update else []
        self.allow_half_getting = allow_half_getting
        self.on_shift_click = on_shift_click
        self.amount_lable = pyglet.text.Label(text=str(self.master.itemstack.amount), anchor_x="right")

    def get_allowed_item_tags(self):
        return self.master.allowed_item_tags

    def set_allowed_item_tags(self, tags: list):
        self.master.allowed_item_tags = tags

    allowed_item_tags = property(get_allowed_item_tags, set_allowed_item_tags)

    def get_itemstack(self):
        return self.master.itemstack

    def set_itemstack(self, stack, **kwargs):
        self.master.set_itemstack(stack, **kwargs)

    def call_update(self, player=False):
        self.master.call_update(player=player)

    itemstack = property(get_itemstack, set_itemstack)

    def copy(self, position=(0, 0)):
        return self.master.copy(position=position)

    def draw(self, dx=0, dy=0, hovering=False):
        """
        draws the slot
        """
        if hovering:
            PYGLET_IMAGE_HOVERING.position = (self.position[0] + dx, self.position[1] + dy)
            PYGLET_IMAGE_HOVERING.draw()
        if self.itemstack.item and self.itemstack.item.get_default_item_image_location() != self.__last_itemfile:
            pos, index = item.ItemHandler.items.get_attribute("itemindextable")[self.itemstack.item.get_name()][
                self.itemstack.item.get_active_image_location()]
            image = item.ItemHandler.TEXTURE_ATLASES[index].group[tuple(pos)]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        elif not self.itemstack.item:
            self.sprite = None
        if self.sprite:
            self.sprite.position = (self.position[0] + dx, self.position[1] + dy)
            self.sprite.draw()
            if self.itemstack.amount != 1:
                self.amount_lable.text = str(self.itemstack.amount)
                self.amount_lable.x = self.position[0] + SLOT_WIDTH
                self.amount_lable.y = self.position[1] - dy
                self.amount_lable.draw()
        self.__last_itemfile = self.itemstack.item.get_default_item_image_location() if self.itemstack.item else None

    def draw_lable(self, x, y):
        if self.itemstack.amount > 1:
            self.amount_lable.text = str(self.itemstack.amount)
            self.amount_lable.x = self.position[0] + SLOT_WIDTH + x
            self.amount_lable.y = self.position[1] + y
            self.amount_lable.draw()

    def can_set_item(self, itemstack) -> bool: return self.master.can_set_item(itemstack)

