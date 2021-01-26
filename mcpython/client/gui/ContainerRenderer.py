"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import typing
from abc import ABC

from mcpython import shared, logger
import pyglet
import mcpython.ResourceLoader
import mcpython.util.texture
import PIL.Image
import uuid
import random


class ContainerRenderer(ABC):
    """
    Base class for rendering a container at the client
    Client-only code
    """

    @staticmethod
    def get_config_file() -> typing.Optional[str]:
        """
        :return: the location of the inventory config file (if provided)
        """

    def __init__(self, container=None):
        self.container = container
        self.active = False
        self.bg_sprite: typing.Optional[pyglet.sprite.Sprite] = None
        self.bg_image_size = None
        self.bg_anchor = "MM"
        self.window_anchor = "MM"
        self.position = (0, 0)
        self.bg_image_pos = (0, 0)
        shared.inventory_handler.add(self)
        self.slots = self.create_slot_renderers()
        self.config = {}  # todo: add special class holding this information with serializer for it
        self.reload_config()
        self.custom_name = None  # the custom name; If set, rendered in the inventory
        self.custom_name_label = pyglet.text.Label()
        self.custom_name_label.anchor_y = "top"
        self.custom_name_label.color = (0, 0, 0, 255)

    def reload_config(self):
        """
        Reload the config file
        """
        if self.get_config_file() is not None:
            try:
                self.config = mcpython.ResourceLoader.read_json(self.get_config_file())
            except:
                logger.print_exception(
                    "[FATAL] failed to load inventory config file {} for inventory {}".format(
                        self.get_config_file(), self
                    )
                )
                self.config = {}
                self.on_reload()
                return
        else:
            self.config = {}
            self.on_reload()
            return

        for raw_slot_id in self.config["slots"] if "slots" in self.config else []:
            slot_id = int(raw_slot_id)
            entry = self.config["slots"][raw_slot_id]

            if "position" in entry:
                x, y = tuple(entry["position"])
                self.slots[slot_id].position = x, y

            if "allow_player_insert" in entry:
                self.slots[slot_id].interaction_mode[1] = entry["allow_player_insert"]

            if "allow_player_remove" in entry:
                self.slots[slot_id].interaction_mode[0] = entry["allow_player_remove"]

            if "allow_player_add_to_free_place" in entry:
                self.slots[slot_id].interaction_mode[2] = entry[
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
                    self.slots[slot_id].empty_image = pyglet.sprite.Sprite(image)
                except:
                    logger.print_exception(
                        "[FATAL] failed to load empty slot image from {}".format(
                            entry["empty_slot_image"]
                        )
                    )

            if "allowed_tags" in entry:
                self.slots[slot_id].allowed_item_tags = entry["allowed_tags"]

        if "image_size" in self.config:
            self.bg_image_size = tuple(self.config["image_size"])

        if "image_anchor" in self.config:
            self.bg_anchor = self.config["image_anchor"]

        if "window_anchor" in self.config:
            self.window_anchor = self.config["window_anchor"]

        if "image_position" in self.config:
            self.position = self.config["image_position"]

        if "image_location" in self.config:
            try:
                if mcpython.ResourceLoader.exists(self.config["image_location"]):
                    self.bg_sprite = pyglet.sprite.Sprite(
                        mcpython.ResourceLoader.read_pyglet_image(
                            self.config["image_location"]
                        )
                    )
                else:
                    self.bg_sprite = pyglet.sprite.Sprite(
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

    def tick(self, dt: float):
        pass

    def create_slot_renderers(self) -> list:
        """
        Creates the slots
        :return: the slots the inventory uses
        """
        return []

    def get_position(self):
        """
        :return: the position of the inventory
        todo: add cache
        todo: recalculate on resize than
        """
        x, y = self.position
        wx, wy = shared.window.get_size()
        sx, sy = self.bg_image_size if self.bg_image_size is not None else (0, 0)

        if self.bg_anchor[0] == "M":
            x -= sx // 2
        elif self.bg_anchor[0] == "R":
            x -= sx
        if self.bg_anchor[1] == "M":
            y -= sy // 2
        elif self.bg_anchor[1] == "U":
            y -= sy
        if self.window_anchor[0] == "M":
            x += wx // 2
        elif self.window_anchor[0] == "R":
            x = wx - abs(x)
        if self.window_anchor[1] == "M":
            y += wy // 2
        elif self.window_anchor[1] == "U":
            y = wy - abs(y)

        return x, y

    def on_activate(self):
        """
        Called when the inventory is shown
        """

    def on_deactivate(self):
        """
        Called when the inventory is hidden
        """

    def is_closable_by_escape(self) -> bool:
        return True

    def is_always_open(self) -> bool:
        return False

    def is_blocking_interactions(self) -> bool:
        return True

    def get_draw_slots(self):
        """
        Helper function for getting the slots to draw on screen
        """
        return self.get_interaction_slots()

    def draw(self, hovering_slot=None):
        """
        Draws the inventory
        Feel free to copy code into your own inventory and write your rendering around it
        """
        x, y = self.get_position()
        if self.bg_sprite is not None:
            self.bg_sprite.position = (
                x + self.bg_image_pos[0],
                y + self.bg_image_pos[1],
            )
            self.bg_sprite.draw()

        for slot in self.get_draw_slots():
            slot.draw(x, y, hovering=slot == hovering_slot)

        for slot in self.get_draw_slots():
            slot.draw_label()

        if self.custom_name is not None:
            if self.custom_name_label.text != self.custom_name:
                self.custom_name_label.text = self.custom_name

            self.custom_name_label.x = x + 15
            self.custom_name_label.y = y + self.bg_image_size[1] - 10
            self.custom_name_label.draw()

    # todo: remove
    def on_world_cleared(self):
        [slot.get_itemstack().clean() for slot in self.slots]
        if self in shared.inventory_handler.opened_inventory_stack:
            shared.inventory_handler.hide(self)

    def get_interaction_slots(self):
        return self.slots

    # todo: remove
    def clear(self):
        for slot in self.slots:
            slot.get_itemstack().clean()

    # todo: add option if container should be copied
    def copy(self):
        obj = self.__class__()
        for i in range(3 * 9):
            obj.slots[i].set_itemstack(self.slots[i].get_itemstack().copy())
        return obj

    def load(self, data) -> bool:
        """
        Deserializes the data into the inventory
        :param data: the data saved
        :return: if load is valid or not
        """
        return True

    def post_load(self, data):
        """
        Deserializes stuff after the the slot data is loaded
        :param data: the data stored
        """

    def save(self):
        """
        Serializes the inventory into an pickle-able data stream
        :return: the data
        """
        return "no:data"

    def insert_items(
        self, items: list, random_check_order=False, insert_when_same_item=True
    ) -> list:
        skipped = []
        while len(items) > 0:
            stack = items.pop(0)
            if not self.insert_item(
                stack,
                random_check_order=random_check_order,
                insert_when_same_item=insert_when_same_item,
            ):
                skipped.append(stack)
        return skipped

    def insert_item(
        self, itemstack, random_check_order=False, insert_when_same_item=True
    ) -> bool:
        if itemstack.is_empty():
            return True
        slots = self.slots.copy()
        if random_check_order:
            random.shuffle(slots)
        for slot in slots:
            if slot.itemstack.is_empty():
                slot.set_itemstack(itemstack)
                return True
            elif slot.itemstack.get_item_name() == itemstack.get_item_name():
                if (
                    slot.itemstack.amount + itemstack.amount
                    <= itemstack.item.STACK_SIZE
                ):
                    slot.itemstack.add_amount(itemstack.amount)
                    return True
                elif insert_when_same_item:
                    overflow = itemstack.amount - (
                        itemstack.item.STACK_SIZE - slot.itemstack.amount
                    )
                    slot.itemstack.amount = itemstack.item.STACK_SIZE
                    itemstack.set_amount(overflow)
        return False

    def update_shift_container(self):
        """
        called when the inventory should update the content of the ShiftContainer of the inventory-handler
        """
