"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import pyglet
import mcpython.ResourceLoader
import mcpython.util.texture
import PIL.Image
import uuid
import random
import deprecation


class Inventory:
    """
    base inventory class
    todo: split up into the storage part and the rendering part
    """

    @staticmethod
    def get_config_file() -> str:
        """
        :return: the location of the inventory config file (if provided)
        """

    def __init__(self):
        self.active = False
        self.bgsprite: pyglet.sprite.Sprite = None
        self.bgimagesize = None
        self.bganchor = "MM"
        self.windowanchor = "MM"
        self.position = (0, 0)
        self.bg_image_pos = (0, 0)
        G.inventoryhandler.add(self)
        self.slots = self.create_slots()
        self.config = {}
        self.reload_config()
        self.uuid = uuid.uuid4()

    def reload_config(self):
        """
        reload the config file
        todo: make public
        """
        if self.get_config_file():
            try:
                self.config = mcpython.ResourceLoader.read_json(self.get_config_file())
            except:
                logger.print_exception(
                    "[FATAL] failed to load inventory config file {} for inventory {}".format(
                        self.get_config_file(), self
                    )
                )
        else:
            self.config = {}
            self.on_reload()
            return
        for slotid in self.config["slots"] if "slots" in self.config else []:
            sid = int(slotid)
            entry = self.config["slots"][slotid]
            if "position" in entry:
                # logger.println(sid, entry)
                self.slots[sid].position = tuple(entry["position"])
            if "allow_player_insert" in entry:
                self.slots[sid].interaction_mode[1] = entry["allow_player_insert"]
            if "allow_player_remove" in entry:
                self.slots[sid].interaction_mode[0] = entry["allow_player_remove"]
            if "allow_player_add_to_free_place" in entry:
                self.slots[sid].interaction_mode[2] = entry[
                    "allow_player_add_to_free_place"
                ]
            if "empty_slot_image" in entry:
                try:
                    image = mcpython.ResourceLoader.read_image(
                        entry["empty_slot_image"]
                    )
                    image = mcpython.util.texture.to_pyglet_image(
                        image.resize((32, 32), PIL.Image.NEAREST)
                    )
                    self.slots[sid].empty_image = pyglet.sprite.Sprite(image)
                except:
                    logger.print_exception(
                        "[FATAL] failed to load empty slot image from {}".format(
                            entry["empty_slot_image"]
                        )
                    )
            if "allowed_tags" in entry:
                self.slots[sid].allowed_item_tags = entry["allowed_tags"]
        if "image_size" in self.config:
            self.bgimagesize = tuple(self.config["image_size"])
        if "image_anchor" in self.config:
            self.bganchor = self.config["image_anchor"]
        if "window_anchor" in self.config:
            self.windowanchor = self.config["window_anchor"]
        if "image_position" in self.config:
            self.position = self.config["image_position"]
        if "image_location" in self.config:
            try:
                if mcpython.ResourceLoader.exists(self.config["image_location"]):
                    self.bgsprite = pyglet.sprite.Sprite(
                        mcpython.ResourceLoader.read_pyglet_image(
                            self.config["image_location"]
                        )
                    )
                else:
                    self.bgsprite = pyglet.sprite.Sprite(
                        mcpython.ResourceLoader.read_pyglet_image(
                            "assets/missing_texture.png"
                        )
                    )
            except:
                logger.print_exception(
                    "[FATAL] failed to load background image {}".format(
                        self.config["image_location"]
                    )
                )
        if "bg_image_pos" in self.config:
            self.bg_image_pos = tuple(self.config["bg_image_pos"])
        self.on_reload()

    def on_reload(self):
        pass

    def create_slots(self) -> list:  # todo: remove
        """
        creates the slots
        :return: the slots the inventory uses
        """
        return []

    @deprecation.deprecated("dev1-2", "a1.3.0")
    def _get_position(self):
        return self.get_position()

    def get_position(self):
        """
        :return: the position of the inventory
        """
        x, y = self.position
        wx, wy = G.window.get_size()
        sx, sy = self.bgimagesize if self.bgsprite else (0, 0)
        if self.bganchor[0] == "M":
            x -= sx // 2
        elif self.bganchor[0] == "R":
            x -= sx
        if self.bganchor[1] == "M":
            y -= sy // 2
        elif self.bganchor[1] == "U":
            y -= sy
        if self.windowanchor[0] == "M":
            x += wx // 2
        elif self.windowanchor[0] == "R":
            x = wx - abs(x)
        if self.windowanchor[1] == "M":
            y += wy // 2
        elif self.windowanchor[1] == "U":
            y = wy - abs(y)
        return x, y

    def activate(self):  # todo: remove
        G.inventoryhandler.show(self)

    def deactivate(self):  # todo: remove
        G.inventoryhandler.hide(self)

    def on_activate(self):
        """
        called when the inventory is shown
        """

    def on_deactivate(self):
        """
        called when the inventory is hidden
        """

    def is_closable_by_escape(self) -> bool:
        return True  # todo: make attribute

    def is_always_open(self) -> bool:
        return False  # todo: make attribute

    def draw(self, hoveringslot=None):
        """
        draws the inventory
        """
        self.on_draw_background()
        x, y = self._get_position()
        if self.bgsprite:
            self.bgsprite.position = (
                x + self.bg_image_pos[0],
                y + self.bg_image_pos[1],
            )
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()
        for slot in self.slots:
            slot.draw(x, y, hovering=slot == hoveringslot)
        self.on_draw_over_image()
        for slot in self.slots:
            slot.draw_label()
        self.on_draw_overlay()

    def on_draw_background(self):  # todo: remove
        """
        draw the background
        """

    def on_draw_over_backgroundimage(self):  # todo: remove
        """
        draw between background and slots
        """

    def on_draw_over_image(self):  # todo: remove
        """
        draw between slots and counts
        """

    def on_draw_overlay(self):  # todo: remove
        """
        draw over anything else
        """

    def is_blocking_interactions(self) -> bool:  # todo: make attribute
        return True

    def on_world_cleared(self):  # todo: remove
        [slot.get_itemstack().clean() for slot in self.slots]
        if self in G.inventoryhandler.opened_inventorystack:
            G.inventoryhandler.hide(self)

    def get_interaction_slots(self):  # todo: make attribute
        return self.slots

    def clear(self):
        for slot in self.slots:
            slot.get_itemstack().clean()

    def copy(self):
        obj = self.__class__()
        for i in range(3 * 9):
            obj.slots[i].set_itemstack(self.slots[i].get_itemstack().copy())
        return obj

    def load(self, data) -> bool:
        """
        serializes the data into the inventory
        :param data: the data saved
        :return: if load is valid or not
        """
        return True

    def post_load(self, data):
        """
        serializes stuff after the the slot data is loaded
        :param data: the data stored
        """

    def save(self):
        """
        serializes the inventory into an pickle-able data stream
        :return: the data
        """
        return "no:data"

    def insert_items(
        self, items: list, random_check_order=False, insert_when_same_item=True
    ):
        while len(items) > 0:
            self.insert_item(
                items.pop(0),
                random_check_order=random_check_order,
                insert_when_same_item=insert_when_same_item,
            )

    def insert_item(
        self, itemstack, random_check_order=False, insert_when_same_item=True
    ):
        if itemstack.is_empty():
            return
        slots = self.slots.copy()
        if random_check_order:
            random.shuffle(slots)
        for slot in slots:
            if slot.itemstack.is_empty():
                slot.set_itemstack(itemstack)
                return
            elif slot.itemstack.get_item_name() == itemstack.get_item_name():
                if (
                    slot.itemstack.amount + itemstack.amount
                    <= itemstack.item.STACK_SIZE
                ):
                    slot.itemstack.add_amount(itemstack.amount)
                    return
                elif insert_when_same_item:
                    overflow = itemstack.amount - (
                        itemstack.item.STACK_SIZE - slot.itemstack.amount
                    )
                    slot.itemstack.amount = itemstack.item.STACK_SIZE
                    itemstack.set_amount(overflow)
        logger.println("itemstack overflow: ".format(itemstack))

    def update_shift_container(self):
        """
        called when the inventory should update the content of the ShiftContainer of the inventory-handler
        """

    def __del__(self):
        # we do not care about it when it is None [gc-sided deletion at the end of the program]
        if G is None or G.inventoryhandler is None:
            return
        if self in G.inventoryhandler.alwaysopened:
            G.inventoryhandler.alwaysopened.remove(self)
        G.inventoryhandler.hide(self)
        if self in G.inventoryhandler.inventorys:
            G.inventoryhandler.inventorys.remove(self)
        G.inventoryhandler.update_shift_container()
