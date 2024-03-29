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

# todo: split container part & rendering part
import typing
from abc import ABC

import mcpython.common.item.ItemManager
import mcpython.engine.ResourceLoader
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.engine import logger
from mcpython.engine.network.util import IBufferSerializeAble, ReadBuffer, WriteBuffer

if shared.IS_CLIENT:
    import pyglet
    from mcpython.client.texture.TextureAtlas import MISSING_TEXTURE
    from mcpython.util.texture import to_pyglet_image


SLOT_WIDTH = 32

if shared.IS_CLIENT and not shared.IS_TEST_ENV:
    PYGLET_IMAGE_HOVERING = pyglet.sprite.Sprite(
        asyncio.run(
            mcpython.engine.ResourceLoader.read_pyglet_image(
                "assets/minecraft/textures/gui/hotbar_selected.png"
            )
        )
    )
else:
    PYGLET_IMAGE_HOVERING = None


class ISlot(IBufferSerializeAble, ABC):
    """
    Base class for everything slot-like
    Provides some API for interaction with the user
    """

    def __init__(self):
        self.on_update = []
        self.assigned_inventory = None

    async def handle_shift_click(
        self, x: int, y: int, button: int, modifiers: int, player
    ):
        pass

    async def handle_click(self, button: int, modifiers: int) -> bool:
        return False

    def get_capacity(self) -> int:
        raise NotImplementedError()

    def get_itemstack(self) -> ItemStack:
        raise NotImplementedError()

    def set_itemstack(
        self,
        stack: ItemStack,
        update=True,
        player=False,
    ):
        raise NotImplementedError()

    def set_itemstack_force(self, *args, **kwargs):
        self.set_itemstack(*args, **kwargs)

    def call_update(self, player=False):
        pass

    async def call_update_async(self, player=False):
        return self.call_update(player=player)

    def copy(self, position=(0, 0)):
        raise NotImplementedError()

    def deepCopy(self):
        raise NotImplementedError()

    def draw(self, dx=0, dy=0, hovering=False, center_position=None):
        pass

    def draw_label(self, x=None, y=None):
        pass

    def is_item_allowed(self, itemstack: ItemStack) -> bool:
        raise NotImplementedError()

    def getParent(self) -> "ISlot":
        raise NotImplementedError()

    def clean_itemstack(self):
        self.get_itemstack().clean()

    def invalidate(self):
        pass


class Slot(ISlot):
    """
    Basic slot class
    """

    def __init__(
        self,
        itemstack: ItemStack = None,
        position: typing.Tuple[int, int] = (0, 0),
        allow_player_remove=True,
        allow_player_insert=True,
        allow_player_add_to_free_place=True,
        allow_half_getting=True,
        allowed_item_tags: typing.Optional[typing.List[str]] = None,
        disallowed_item_tags: typing.Optional[typing.List[str]] = None,
        allowed_item_test: typing.Optional[typing.Callable] = None,
        on_update: typing.Optional[typing.Callable] = None,
        on_shift_click: typing.Optional[typing.Callable] = None,
        on_button_press: typing.Optional[typing.Callable] = None,
        on_click_on_slot: typing.Optional[typing.Callable] = None,
        empty_image: typing.Optional = None,
        enable_hovering_background=True,
        capacity: typing.Optional[int] = None,
        check_function=None,
    ):
        """
        Creates a new slot
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
        :param check_function: a function to check if the item is valid, signature: (Slot, ItemStack) -> bool
        :param on_click_on_slot: a function invoked with button & modifiers when the player pressed on the slot
        """
        super().__init__()

        self.__itemstack = itemstack if itemstack else ItemStack.create_empty()

        self.position = position
        if self.__itemstack.item and shared.IS_CLIENT:
            pos, index = mcpython.common.item.ItemManager.items.item_index_table[
                self.__itemstack.get_item_name()
            ][self.__itemstack.item.get_active_image_location()]
            image = mcpython.common.item.ItemManager.ITEM_ATLAS.atlases[index].group[
                tuple(pos)
            ]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)
        else:
            self.sprite = None

        if shared.IS_CLIENT:
            self.amount_label = pyglet.text.Label(
                text=str(self.itemstack.amount), anchor_x="right"
            )
            self.__last_item_file = (
                self.__itemstack.item.get_default_item_image_location()
                if self.__itemstack.item
                else None
            )
            self.amount_label = pyglet.text.Label()

        # todo: make separated attributes
        self.interaction_mode = [
            allow_player_remove,
            allow_player_insert,
            allow_player_add_to_free_place,
            allow_half_getting,
        ]
        self.on_update = [on_update] if on_update else []
        self.allow_half_getting = allow_half_getting
        self.on_shift_click = on_shift_click
        self.children = []

        if shared.IS_CLIENT:
            self.empty_image = (
                pyglet.sprite.Sprite(empty_image) if empty_image else None
            )

        self.on_click_on_slot = on_click_on_slot

        self.allowed_item_tags = allowed_item_tags
        self.disallowed_item_tags = disallowed_item_tags
        self.allowed_item_func = allowed_item_test
        self.enable_hovering_background = enable_hovering_background

        self.on_button_press = on_button_press
        self.__capacity = capacity
        self.check_function = check_function

    async def handle_click(self, button: int, modifiers: int) -> bool:
        return self.on_click_on_slot and self.on_click_on_slot(self, button, modifiers)

    async def handle_shift_click(
        self, x: int, y: int, button: int, modifiers: int, player
    ) -> bool:
        if self.on_shift_click:
            result = self.on_shift_click(self, x, y, button, modifiers, player)
            if isinstance(result, typing.Awaitable):
                return await result
            return result
        return True

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await self.itemstack.read_from_network_buffer(buffer)

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await self.itemstack.write_to_network_buffer(buffer)

    def get_capacity(self) -> int:
        return (
            self.__capacity
            if self.__capacity is not None
            else (64 if self.itemstack.is_empty() else self.itemstack.item.STACK_SIZE)
        )

    def get_itemstack(self) -> ItemStack:
        return self.__itemstack

    def get_linked_itemstack_for_sift_clicking(self):
        return self.itemstack

    def set_itemstack(
        self,
        stack: ItemStack,
        update=True,
        player=False,
    ):
        self.__itemstack = stack if stack is not None else ItemStack.create_empty()
        if update:
            self.call_update(player=player)

    def call_update(self, player=False):
        for f in self.on_update:
            try:
                result = f(player=player)
                if isinstance(result, typing.Awaitable):
                    shared.tick_handler.schedule_once(result)
            except:  # lgtm [py/catch-base-exception]
                logger.print_exception(
                    "during invoking {} for slot-update of {}".format(f, self)
                )

    async def call_update_async(self, player=False):
        for f in self.on_update:
            try:
                result = f(player=player)
                if isinstance(result, typing.Awaitable):
                    await result
            except:  # lgtm [py/catch-base-exception]
                logger.print_exception(
                    "during invoking {} for slot-update of {}".format(f, self)
                )

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
        This will copy the content of the slot into a Slot-object
        """
        return Slot(
            self.itemstack,
            self.position,
            self.interaction_mode[0],
            self.interaction_mode[1],
            self.interaction_mode[2],
            self.interaction_mode[3],
            self.allowed_item_tags,
            self.disallowed_item_tags,
            self.allowed_item_func,
            self.on_update,
            self.on_shift_click,
            self.on_button_press,
            self.on_click_on_slot,
            self.empty_image,
            self.enable_hovering_background,
            self.get_capacity(),
            self.check_function,
        )

    def draw(self, dx=0, dy=0, hovering=False, center_position=None):
        """
        Draws the slot
        """
        if center_position is None:
            center_position = self.position

        if hovering and self.enable_hovering_background:
            PYGLET_IMAGE_HOVERING.position = (
                center_position[0] + dx,
                center_position[1] + dy,
            )
            PYGLET_IMAGE_HOVERING.draw()

        if (
            not self.itemstack.is_empty()
            and (
                self.itemstack.item.get_default_item_image_location()
                != self.__last_item_file
                or self.sprite is None
            )
            and shared.IS_CLIENT
        ):
            image = mcpython.common.item.ItemManager.items.item_index_table.setdefault(
                self.itemstack.get_item_name(), {}
            ).setdefault(
                self.itemstack.item.get_active_image_location(),
                to_pyglet_image(MISSING_TEXTURE.resize((32, 32))),
            )
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)

        elif self.itemstack.is_empty():
            self.sprite = None
            if self.empty_image is not None:
                self.empty_image.position = (
                    center_position[0] + dx,
                    center_position[1] + dy,
                )
                self.empty_image.draw()

        if self.sprite:
            self.sprite.position = (center_position[0] + dx, center_position[1] + dy)
            self.sprite.draw()

        if not self.itemstack.is_empty():
            self.itemstack.item.draw_in_inventory(
                self.itemstack, (center_position[0] + dx, center_position[1] + dy), 1
            )

        self.__last_item_file = (
            self.itemstack.item.get_default_item_image_location()
            if self.itemstack.item
            else None
        )

    def draw_label(self, x=None, y=None):
        """
        these code draws only the label, before, normal draw should be executed for correct setup
        """
        if self.itemstack.amount > 1:
            if self.sprite is None:
                return
            # don't know why this is needed, but it is needed for fixing issue 106
            self.amount_label.anchor_x = "right"

            self.amount_label.text = str(self.itemstack.amount)
            self.amount_label.x = (self.sprite.x + SLOT_WIDTH) if x is None else x
            self.amount_label.y = self.sprite.y if y is None else y
            self.amount_label.draw()

    def is_item_allowed(self, itemstack: ItemStack) -> bool:
        if callable(self.check_function):
            if not self.check_function(self, itemstack):
                return False

        any_tag_set = (
            self.allowed_item_tags is not None or self.disallowed_item_tags is not None
        )
        has_correct_tag = itemstack.item is not None and (
            (
                self.allowed_item_tags is not None
                and any([x in itemstack.item.TAGS for x in self.allowed_item_tags])
            )
            or (
                self.disallowed_item_tags is not None
                and any(
                    [x not in itemstack.item.TAGS for x in self.disallowed_item_tags]
                )
            )
        )
        has_allowed_func = self.allowed_item_func is not None
        check_allowed_func = has_allowed_func and self.allowed_item_func(itemstack)

        return (
            not (any_tag_set or has_allowed_func)
            or (any_tag_set and has_correct_tag)
            or check_allowed_func
        )

    def __str__(self):
        return "Slot(position=({},{}),itemstack={},memory={})".format(
            *self.position, self.itemstack, hex(id(self))
        )

    def __repr__(self):
        return str(self)

    def getParent(self):
        return self


class SlotCopy(ISlot):
    def get_capacity(self) -> int:
        return self.master.get_capacity()

    def deepCopy(self):
        return self.master.deepCopy()

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
        on_click_on_slot=None,
    ):
        super().__init__()
        # todo: add empty image
        # todo: add options for item allowing
        self.master: Slot = master
        self.position = position
        if self.master and self.get_itemstack().item and shared.IS_CLIENT:
            pos, index = mcpython.common.item.ItemManager.items.item_index_table[
                self.get_itemstack().get_item_name()
            ][self.get_itemstack().item.get_active_image_location()]
            image = mcpython.common.item.ItemManager.ITEM_ATLAS.atlases[index].group[
                tuple(pos)
            ]
            self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(image)

        else:
            self.sprite = None

        self.__last_item_file = (
            self.itemstack.item.get_default_item_image_location()
            if self.master and self.itemstack.item
            else None
        )
        self.interaction_mode = [
            allow_player_remove,
            allow_player_insert,
            allow_player_add_to_free_place,
        ]
        self.on_update = [on_update] if on_update else []
        self.on_click_on_slot = on_click_on_slot
        self.allow_half_getting = allow_half_getting
        self.on_shift_click = on_shift_click

        if shared.IS_CLIENT:
            self.amount_label = pyglet.text.Label(
                text=str(self.master.itemstack.amount) if self.master else "-",
                anchor_x="right",
            )

        self.on_button_press = on_button_press
        self.slot_position = 0, 0

    def get_linked_itemstack_for_sift_clicking(self):
        return self.get_itemstack()

    async def handle_click(self, button: int, modifiers: int) -> bool:
        return self.on_click_on_slot and self.on_click_on_slot(self, button, modifiers)

    def get_allowed_item_tags(self):
        return self.master.allowed_item_tags

    def set_allowed_item_tags(self, tags: list):
        self.master.allowed_item_tags = tags

    allowed_item_tags = property(get_allowed_item_tags, set_allowed_item_tags)

    def get_itemstack(self) -> ItemStack:
        return (
            self.master.itemstack
            if self.master is not None
            else ItemStack.create_empty()
        )

    def set_itemstack(self, stack, **kwargs):
        self.master.set_itemstack(stack, **kwargs)

    def call_update(self, player=False):
        self.master.call_update(player=player)

    async def call_update_async(self, player=False):
        return await self.master.call_update_async(player=player)

    itemstack = property(get_itemstack, set_itemstack)

    def copy(self, position=(0, 0)):
        return self.master.copy(position=position)

    def draw(self, dx=0, dy=0, hovering=False, center_position=None):
        self.master.draw(dx, dy, hovering, center_position=self.position)
        self.slot_position = dx, dy

    def draw_label(self, x=None, y=None):
        self.master.draw_label(
            x
            if x is not None
            else self.slot_position[0] + self.position[0] + SLOT_WIDTH,
            y if y is not None else self.slot_position[1] + self.position[1],
        )

    def is_item_allowed(self, itemstack) -> bool:
        return self.master.is_item_allowed(itemstack)

    def __str__(self):
        return "SlotCopy(position=({},{}),of={},memory={})".format(
            *self.position, self.master, hex(id(self))
        )

    def __repr__(self):
        return str(self)

    def getParent(self):
        return self.master


class SlotCopyWithDynamicTarget(SlotCopy):
    def __init__(
        self,
        getter: typing.Callable[[], ISlot],
        position=(0, 0),
        allow_player_remove=True,
        allow_player_insert=True,
        allow_player_add_to_free_place=True,
        on_update=None,
        on_click_on_slot=None,
        allow_half_getting=True,
        on_shift_click=None,
        on_button_press=None,
    ):
        self.slot_position = 0, 0
        self.getter = getter
        self.valid = False
        self.cached_master = None
        self.position = position
        self.__last_item_file = (
            self.itemstack.item.get_default_item_image_location()
            if self.master and self.itemstack.item
            else None
        )
        self.interaction_mode = [
            allow_player_remove,
            allow_player_insert,
            allow_player_add_to_free_place,
        ]
        self.on_update = [on_update] if on_update else []
        self.on_click_on_slot = on_click_on_slot
        self.allow_half_getting = allow_half_getting
        self.on_shift_click = on_shift_click

        if shared.IS_CLIENT:
            self.amount_label = pyglet.text.Label(
                text=str(self.master.get_itemstack().amount) if self.master else "-",
                anchor_x="right",
            )
        self.on_button_press = on_button_press

    def invalidate(self):
        self.valid = False

    def get_master(self):
        if self.valid:
            return self.cached_master
        self.cached_master = self.getter()
        self.valid = True
        return self.cached_master

    master = property(get_master)


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
        allow_player_override_delete=True,
    ):
        super().__init__(
            itemstack=itemstack,
            position=position,
            allow_player_remove=allow_player_remove,
            allow_player_insert=allow_player_override_delete,
            allow_player_add_to_free_place=allow_player_add_to_free_place,
            on_update=on_update,
            allow_half_getting=allow_half_getting,
            on_shift_click=on_shift_click,
            on_button_press=on_button_press,
        )
        self.reference_stack = self.itemstack.copy()

    def set_itemstack(self, stack, update=True, player=False):
        stack.clean()

    def clean_itemstack(self):
        pass

    def set_itemstack_force(self, stack):
        super().set_itemstack(stack.copy().set_amount(1))
        self.reference_stack = stack.copy().set_amount(1)
        return self

    def call_update(self, player=False):
        [f(player=player) for f in self.on_update]
        self.itemstack.add_amount(0)
        if (
            self.itemstack.get_item_name() != self.reference_stack.get_item_name()
            or self.itemstack.amount == 0
        ):
            self.itemstack = self.reference_stack.copy()
        self.itemstack.set_amount(1)
        self.reference_stack.set_amount(1)

    def get_linked_itemstack_for_sift_clicking(self):
        return (
            self.itemstack.copy().set_amount(self.itemstack.item.STACK_SIZE)
            if not self.get_itemstack().is_empty()
            else None
        )

    itemstack = property(Slot.get_itemstack, set_itemstack)

    def __repr__(self):
        return f"InfiniteSlot(item='{self.reference_stack.get_item_name()}',visible='{self.itemstack.get_item_name()}',position={self.position})'"

    def __str__(self):
        return repr(self)

    def is_item_allowed(self, itemstack: ItemStack) -> bool:
        return True


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

    def set_itemstack(
        self,
        stack: ItemStack,
        update=True,
        player=False,
    ):
        self.__itemstack = stack if stack is not None else ItemStack.create_empty()
        if not stack.is_empty():
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
        self.__itemstack = stack if stack else ItemStack.create_empty()
        flag = True
        if update:
            flag = self.call_update(player=player)
        if flag is not False:
            self.__itemstack.clean()
