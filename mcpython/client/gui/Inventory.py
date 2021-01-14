"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

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
        self.bg_sprite: pyglet.sprite.Sprite = None
        self.bg_image_size = None
        self.bg_anchor = "MM"
        self.window_anchor = "MM"
        self.position = (0, 0)
        self.bg_image_pos = (0, 0)
        G.inventory_handler.add(self)
        self.slots = self.create_slots()
        self.config = {}
        self.reload_config()
        self.uuid = uuid.uuid4()
        self.custom_name = None

    def reload_config(self):
        """
        reload the config file
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
        else:
            self.config = {}
            self.on_reload()
            return
        for slotid in self.config["slots"] if "slots" in self.config else []:
            sid = int(slotid)
            entry = self.config["slots"][slotid]
            if "position" in entry:
                x, y = tuple(entry["position"])
                self.slots[sid].position = x, y
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

    def create_slots(self) -> list:
        """
        creates the slots
        :return: the slots the inventory uses
        """
        return []

    def get_position(self):
        """
        :return: the position of the inventory
        todo: add cache
        """
        x, y = self.position
        wx, wy = G.window.get_size()
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

    def draw(self, hovering_slot=None):
        """
        Draws the inventory
        Feel free to copy code into your own inventory and write your rendering around it!
        """
        x, y = self.get_position()
        if self.bg_sprite:
            self.bg_sprite.position = (
                x + self.bg_image_pos[0],
                y + self.bg_image_pos[1],
            )
            self.bg_sprite.draw()
        for slot in self.slots:
            slot.draw(x, y, hovering=slot == hovering_slot)
        for slot in self.slots:
            slot.draw_label()

    def is_blocking_interactions(self) -> bool:
        return True

    def on_world_cleared(self):  # todo: remove
        [slot.get_itemstack().clean() for slot in self.slots]
        if self in G.inventory_handler.opened_inventory_stack:
            G.inventory_handler.hide(self)

    def get_interaction_slots(self):
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
        # logger.println("itemstack overflow: ".format(itemstack))
        return False

    def update_shift_container(self):
        """
        called when the inventory should update the content of the ShiftContainer of the inventory-handler
        """

    def __del__(self):
        # we do not care about it when it is None [gc-sided deletion at the end of the program]
        if G is None or G.inventory_handler is None:
            return
        if self in G.inventory_handler.always_opened:
            G.inventory_handler.always_opened.remove(self)
        G.inventory_handler.hide(self)
        if self in G.inventory_handler.inventories:
            G.inventory_handler.inventories.remove(self)
        G.inventory_handler.update_shift_container()
