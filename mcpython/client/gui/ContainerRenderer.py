"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import asyncio
import random
import typing
import uuid
from abc import ABC

import mcpython.engine.ResourceLoader
import mcpython.util.texture
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.client.gui.Slot import ISlot
from mcpython.common.container.AbstractContainer import AbstractContainer
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class AbstractContainerRenderer(ABC):
    """
    Base class for a rendering adapter for an AbstractContainer
    Create only on CLIENT! We do not guarantee the existence of pyglet on servers in the future!
    """

    def __init__(self):
        self.container = None

        self.bg_sprite: typing.Optional[pyglet.sprite.Sprite] = None
        self.bg_anchor = "MM"
        self.window_anchor = "MM"
        self.position = (0, 0)
        self.bg_image_pos = (0, 0)
        self.custom_name_label = pyglet.text.Label(color=(255, 255, 255, 255))
        self.custom_name_label.anchor_y = "top"

        self.slot_rendering_information = []

    def create_slot_rendering_information(self):
        self.slot_rendering_information.clear()

    def get_position(self):
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

    def bind_container(self, container: AbstractContainer):
        """
        Invoked when a new container should be bound to this renderer
        When multiple containers use the same renderer, this may get invoked more than one time
        """
        self.container = container

    def draw(self):
        position = self.get_position()

        if self.bg_sprite is not None:
            self.bg_sprite.position = position
            self.bg_sprite.draw()

        for slot_rendering in self.slot_rendering_information:
            slot_rendering.draw(position)


class ContainerRenderer(IBufferSerializeAble, ABC):
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
        self.uuid = uuid.uuid4()
        self.slots: typing.List[ISlot] = []

        for slot in self.slots:
            slot.assigned_inventory = self

        # todo: add special class holding this information with serializer for it
        self.config = {}

        # asyncio.get_event_loop().run_until_complete(self.reload_config())
        self.custom_name = None  # the custom name; If set, rendered in the inventory
        self.custom_name_label = pyglet.text.Label(color=(255, 255, 255, 255))
        self.custom_name_label.anchor_y = "top"

        shared.tick_handler.schedule_once(shared.inventory_handler.add(self))

        shared.tick_handler.schedule_once(self.init())
        self.created_slots = False

    async def init(self):
        if self.created_slots:
            return

        self.created_slots = True
        self.slots = await self.create_slot_renderers()

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_bool(self.active)
        buffer.write_string(self.custom_name if self.custom_name is not None else "")

        await buffer.write_list(
            self.slots, lambda slot: slot.write_to_network_buffer(buffer)
        )

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        self.active = buffer.read_bool()

        self.custom_name = buffer.read_string()
        if self.custom_name == "":
            self.custom_name = None
        else:
            self.custom_name_label.text = self.custom_name

        size = buffer.read_int()

        if size != len(self.slots):
            raise RuntimeError(f"invalid slot count received for container {self}!")

        for slot in self.slots:
            await slot.read_from_network_buffer(buffer)

    def on_mouse_button_press(
        self,
        relative_x: int,
        relative_y: int,
        button: int,
        modifiers: int,
        item_stack,
        slot,
    ) -> bool:
        return False

    async def reload_config(self):
        """
        Reload the config file
        """
        if shared.IS_TEST_ENV:
            return

        if self.get_config_file() is not None:
            try:
                self.config = await mcpython.engine.ResourceLoader.read_json(
                    self.get_config_file()
                )
            except:
                logger.print_exception(
                    "[FATAL] failed to load inventory config file '{}' for inventory {}".format(
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

            if slot_id < 0 or slot_id >= len(self.slots):
                logger.println(
                    "[WARN] slot id {} loaded from file {} for inventory instance {} is invalid!".format(
                        slot_id, self.get_config_file(), self
                    )
                )
                continue

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
                    image = await mcpython.engine.ResourceLoader.read_image(
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
                if await mcpython.engine.ResourceLoader.exists(
                    self.config["image_location"]
                ):
                    self.bg_sprite = pyglet.sprite.Sprite(
                        await mcpython.engine.ResourceLoader.read_pyglet_image(
                            self.config["image_location"]
                        )
                    )
                else:
                    self.bg_sprite = pyglet.sprite.Sprite(
                        await mcpython.engine.ResourceLoader.read_pyglet_image(
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

    async def create_slot_renderers(self) -> list:
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

    def is_mouse_in_range(self, x: int, y: int) -> bool:
        px, py = self.get_position()
        sx, sy = self.bg_image_size if self.bg_image_size is not None else (0, 0)

        return 0 <= x - px <= sx and 0 <= y - py <= sy

    async def on_activate(self):
        """
        Called when the inventory is shown
        """

    async def on_deactivate(self):
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
    async def on_world_cleared(self):
        [slot.get_itemstack().clean() for slot in self.slots]
        if self in shared.inventory_handler.open_containers:
            await shared.inventory_handler.hide(self)

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
