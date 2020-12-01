"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals as G, logger
import pyglet
import mcpython.client.gui.ItemStack
import mcpython.common.item.ItemHandler
import mcpython.ResourceLocator
import mcpython.client.rendering.model.ItemModel


SLOT_WIDTH = 32

PYGLET_IMAGE_HOVERING = pyglet.sprite.Sprite(
    mcpython.ResourceLocator.read(
        "assets/minecraft/textures/gui/hotbar_selected.png", "pyglet"
    )
)


class Slot:
    """
    slot class
    """

    def __init__(
        self,
        itemstack=None,
        position=(0, 0),
        allow_player_remove=True,
        allow_player_insert=True,
        allow_player_add_to_free_place=True,
        on_update=None,
        allow_half_getting=True,
        on_shift_click=None,
        empty_image=None,
        allowed_item_tags=None,
        allowed_item_test=None,
        on_button_press=None,
        capacity=None,
        check_function=None,
    ):
        """
        creates an new slot
        :param itemstack: the itemstack to use
        :param position: the position to create at
        :param allow_player_remove: if the player is allowed to remove items out of it
        :param allow_player_insert: if the player is allowed to insert items into it
        :param allow_player_add_to_free_place: if items can be added direct to system
        :param on_update: called when the slot is updated
        :param allow_half_getting: can the player get only the half of the items out of the slot?
        :param on_shift_click: called when shift-clicked on the block, should return if normal logic should go on or not
        :param on_button_press: called when an button is pressed when hovering above the slot
        :param capacity: the max item count for the slot
        :param check_function: an function to check if the item is valid, signature: (Slot, ItemStack) -> bool
        """
        self.__itemstack = (
            itemstack
            if itemstack
            else mcpython.client.gui.ItemStack.ItemStack.get_empty()
        )
        self.position = position
        if self.__itemstack.item:
            pos, index = mcpython.common.item.ItemHandler.items.itemindextable[
                self.__itemstack.get_item_name()
            ][self.__itemstack.item.get_active_image_location()]
            image = mcpython.common.item.ItemHandler.TEXTURE_ATLASES[index].group[
                tuple(pos)
            ]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        else:
            self.sprite = None
        self.amount_label = pyglet.text.Label(
            text=str(self.itemstack.amount), anchor_x="right"
        )
        self.__last_item_file = (
            self.__itemstack.item.get_default_item_image_location()
            if self.__itemstack.item
            else None
        )
        self.interaction_mode = [
            allow_player_remove,
            allow_player_insert,
            allow_player_add_to_free_place,
        ]
        self.on_update = [on_update] if on_update else []
        self.allow_half_getting = allow_half_getting
        self.on_shift_click = on_shift_click
        self.amount_label = pyglet.text.Label()
        self.children = []
        self.empty_image = pyglet.sprite.Sprite(empty_image) if empty_image else None
        self.allowed_item_tags = allowed_item_tags
        self.allowed_item_func = allowed_item_test
        self.on_button_press = on_button_press
        self.__capacity = capacity
        self.check_function = check_function

    def get_capacity(self):
        return (
            self.__capacity
            if self.__capacity is not None
            else (64 if self.itemstack.is_empty() else self.itemstack.item.STACK_SIZE)
        )

    def get_itemstack(self):
        return self.__itemstack

    def set_itemstack(self, stack, update=True, player=False):
        self.__itemstack = (
            stack
            if stack is not None
            else mcpython.client.gui.ItemStack.ItemStack.get_empty()
        )
        if update:
            self.call_update(player=player)

    def call_update(self, player=False):
        for f in self.on_update:
            try:
                f(player=player)
            except:
                logger.print_exception("during invoking {} for slot {}".format(f, self))

    itemstack = property(get_itemstack, set_itemstack)

    def copy(self, position=(0, 0)):
        """
        creates an copy of self
        :param position: the position to create at
        :return: a slotcopy pointing to this
        """
        return SlotCopy(self, position=position)

    def deepCopy(self):
        """
        This will copy the content of the slot into an Slot-object
        """
        return Slot(
            self.itemstack,
            self.position,
            self.interaction_mode[0],
            self.interaction_mode[1],
            self.interaction_mode[2],
            self.on_update,
            self.allow_half_getting,
            self.on_shift_click,
            self.empty_image,
            self.allowed_item_tags,
            self.allowed_item_func,
            self.on_button_press,
            self.__capacity,
            self.check_function,
        )

    def draw(self, dx=0, dy=0, hovering=False):
        """
        draws the slot
        """
        if hovering:
            PYGLET_IMAGE_HOVERING.position = (
                self.position[0] + dx,
                self.position[1] + dy,
            )
            PYGLET_IMAGE_HOVERING.draw()
        if not self.itemstack.is_empty() and (
            self.itemstack.item.get_default_item_image_location()
            != self.__last_item_file
            or self.sprite is None
        ):
            image = mcpython.common.item.ItemHandler.items.itemindextable[
                self.itemstack.get_item_name()
            ][self.itemstack.item.get_active_image_location()]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        elif self.itemstack.is_empty():
            self.sprite = None
            if self.empty_image:
                self.empty_image.position = (
                    self.position[0] + dx,
                    self.position[1] + dy,
                )
                self.empty_image.draw()
        if self.sprite is not None:
            # self.sprite.position = (self.position[0] + dx, self.position[1] + dy)
            # self.sprite.draw()
            mcpython.client.rendering.model.ItemModel.handler.draw(
                self.itemstack.get_item_name(),
                (self.position[0] + dx, self.position[1] + dy),
                "gui",
                {},
            )
        self.__last_item_file = (
            self.itemstack.item.get_default_item_image_location()
            if self.itemstack.item
            else None
        )

    def draw_lable(self, x, y):
        """
        these code draws only the lable, before, normal draw should be executed for correcrt setup
        """
        if self.itemstack.amount > 1:
            if self.sprite is None:
                return
            # don't know why this is needed, but it is needed for fixing issue 106
            self.amount_label.anchor_x = "right"

            self.amount_label.text = str(self.itemstack.amount)
            self.amount_label.x = self.sprite.x + SLOT_WIDTH
            self.amount_label.y = self.sprite.y
            self.amount_label.draw()

    def can_set_item(self, itemstack) -> bool:
        if callable(self.check_function):
            if not self.check_function(self, itemstack):
                return False
        itemname = itemstack.get_item_name()
        flag1 = self.allowed_item_tags is not None
        flag2 = flag1 and (
            any(
                [
                    G.taghandler.has_entry_tag(itemname, "items", x)
                    for x in self.allowed_item_tags
                ]
            )
            or itemstack.get_item_name() is None
        )
        flag3 = self.allowed_item_func is not None
        flag4 = flag3 and self.allowed_item_func(itemstack)
        try:
            return not (flag1 or flag3) or (flag1 and flag2) or (flag3 and flag4)
        except:
            logger.print_exception(
                "[GUI][ERROR] error during executing check func '{}'".format(
                    self.allowed_item_func
                )
            )
            return False

    def save(self):
        d = {
            "itemname": self.itemstack.get_item_name(),
            "amount": self.itemstack.amount,
            "data": None,
        }
        if not self.itemstack.is_empty():
            d["data"] = self.itemstack.item.get_data()
        return {"itemstack": d}

    def load(self, data):
        self.set_itemstack(
            mcpython.client.gui.ItemStack.ItemStack(
                data["itemstack"]["itemname"], data["itemstack"]["amount"]
            )
        )
        if not self.itemstack.is_empty():
            self.itemstack.item.set_data(data["itemstack"]["data"])

    def __str__(self):
        return "Slot(position=({},{}),itemstack={})".format(
            *self.position, self.itemstack
        )

    def __repr__(self):
        return str(self)

    def getParent(self):
        return self


class SlotCopy:
    def __init__(
        self,
        master,
        position=(0, 0),
        allow_player_remove=True,
        allow_player_insert=True,
        allow_player_add_to_free_place=True,
        on_update=None,
        allow_half_getting=True,
        on_shift_click=None,
        on_button_press=None,
    ):
        # todo: add empty image
        # todo: add options for item allowing
        self.master: Slot = master
        self.position = position
        if self.get_itemstack().item:
            pos, index = mcpython.common.item.ItemHandler.items.itemindextable[
                self.get_itemstack().get_item_name()
            ][self.get_itemstack().item.get_active_image_location()]
            image = mcpython.common.item.ItemHandler.TEXTURE_ATLASES[index].group[
                tuple(pos)
            ]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        else:
            self.sprite = None
        self.__last_item_file = (
            self.itemstack.item.get_default_item_image_location()
            if self.itemstack.item
            else None
        )
        self.interaction_mode = [
            allow_player_remove,
            allow_player_insert,
            allow_player_add_to_free_place,
        ]
        self.on_update = [on_update] if on_update else []
        self.allow_half_getting = allow_half_getting
        self.on_shift_click = on_shift_click
        self.amount_label = pyglet.text.Label(
            text=str(self.master.itemstack.amount), anchor_x="right"
        )
        self.on_button_press = on_button_press

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
            PYGLET_IMAGE_HOVERING.position = (
                self.position[0] + dx,
                self.position[1] + dy,
            )
            PYGLET_IMAGE_HOVERING.draw()
        if not self.itemstack.is_empty() and (
            self.itemstack.item.get_default_item_image_location()
            != self.__last_item_file
            or self.sprite is None
        ):
            image = mcpython.common.item.ItemHandler.items.itemindextable[
                self.itemstack.get_item_name()
            ][self.itemstack.item.get_active_image_location()]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        elif self.itemstack.is_empty():
            self.sprite = None
        if self.sprite:
            self.sprite.position = (self.position[0] + dx, self.position[1] + dy)
            self.sprite.draw()
        self.__last_item_file = (
            self.itemstack.item.get_default_item_image_location()
            if self.itemstack.item
            else None
        )

    def draw_lable(self, x, y):
        if self.itemstack.amount > 1:
            self.amount_label.text = str(self.itemstack.amount)
            self.amount_label.x = self.sprite.x + SLOT_WIDTH
            self.amount_label.y = self.sprite.y
            self.amount_label.draw()

    def can_set_item(self, itemstack) -> bool:
        return self.master.can_set_item(itemstack)

    def save(self):
        d = {
            "itemname": self.itemstack.get_item_name(),
            "amount": self.itemstack.amount,
            "data": None,
        }
        if not self.itemstack.is_empty():
            d["data"] = self.itemstack.item.get_data()
        return {"itemstack": d}

    def load(self, data):
        self.set_itemstack(
            mcpython.client.gui.ItemStack.ItemStack(
                data["itemstack"]["itemname"], data["itemstack"]["amount"]
            )
        )
        if not self.itemstack.is_empty():
            self.itemstack.item.set_data(data["itemstack"]["data"])

    def __str__(self):
        return "Slot(position=({},{}),itemstack={},type='copy')".format(
            *self.position, self.itemstack
        )

    def __repr__(self):
        return str(self)

    def getParent(self):
        return self.master


class SlotInfiniteStack(Slot):
    def __init__(
        self,
        itemstack,
        position=(0, 0),
        allow_player_remove=True,
        on_button_press=None,
        allow_player_add_to_free_place=True,
        on_update=None,
        allow_half_getting=True,
        on_shift_click=None,
    ):
        super().__init__(
            itemstack=itemstack,
            position=position,
            allow_player_remove=allow_player_remove,
            allow_player_insert=False,
            allow_player_add_to_free_place=allow_player_add_to_free_place,
            on_update=on_update,
            allow_half_getting=allow_half_getting,
            on_shift_click=on_shift_click,
            on_button_press=on_button_press,
        )
        self.reference_stack = self.itemstack.copy()

    def set_itemstack(self, stack, update=True, player=False):
        pass

    def call_update(self, player=False):
        if not self.on_update:
            return
        [f(player=player) for f in self.on_update]
        if self.itemstack != self.reference_stack:
            self.itemstack.set_itemstack(self.reference_stack.copy())

    itemstack = property(Slot.get_itemstack, set_itemstack)


class SlotInfiniteStackExchangeable(Slot):
    def __init__(
        self,
        itemstack,
        position=(0, 0),
        allow_player_remove=True,
        on_button_press=None,
        allow_player_add_to_free_place=True,
        on_update=None,
        allow_half_getting=True,
        on_shift_click=None,
    ):
        super().__init__(
            itemstack=itemstack,
            position=position,
            allow_player_remove=allow_player_remove,
            allow_player_insert=True,
            allow_player_add_to_free_place=allow_player_add_to_free_place,
            on_update=on_update,
            allow_half_getting=allow_half_getting,
            on_shift_click=on_shift_click,
            on_button_press=on_button_press,
        )
        self.reference_stack = self.itemstack.copy()

    def set_itemstack(self, stack, update=True, player=False):
        self.__itemstack = (
            stack if stack else mcpython.client.gui.ItemStack.ItemStack.get_empty()
        )
        if not stack.itemstack.is_empty():
            self.reference_stack = stack.copy()
        if update:
            self.call_update(player=player)

    def call_update(self, player=False):
        if not self.on_update:
            return
        [f(player=player) for f in self.on_update]
        if self.itemstack != self.reference_stack:
            self.set_itemstack(self.reference_stack.copy())

    itemstack = property(Slot.get_itemstack, set_itemstack)


class SlotTrashCan(Slot):
    def set_itemstack(self, stack, update=True, player=False):
        self.__itemstack = (
            stack if stack else mcpython.client.gui.ItemStack.ItemStack.get_empty()
        )
        flag = True
        if update:
            flag = self.call_update(player=player)
        if flag is not False:
            self.__itemstack.clean()
