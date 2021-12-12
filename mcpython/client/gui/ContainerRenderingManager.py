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
import itertools
import typing

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.HoveringItemBox
import mcpython.client.gui.ShiftContainer
import mcpython.client.gui.Slot
import mcpython.common.state.AbstractStatePart
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.engine import logger
from mcpython.engine.rendering.RenderingLayerManager import MIDDLE_GROUND
from pyglet.window import key, mouse


class OpenedInventoryStatePart(
    mcpython.common.state.AbstractStatePart.AbstractStatePart
):
    """
    Class for inventories as state
    todo: more control to the inventories themselves
    """

    def __init__(self):
        super().__init__()
        self.active = False
        self.slot_list = []
        self.moving_itemstack: typing.Optional[ItemStack] = None

        # The mode for dragging; Possible: 0 - None, 1: equal on all slots, 2: on every slot one more, 3: fill up slots
        self.mode = 0
        self.original_amount: typing.List[int] = []
        self.tool_tip_renderer = (
            mcpython.client.gui.HoveringItemBox.HoveringItemBoxProvider()
        )

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe(MIDDLE_GROUND.getRenderingEvent(), self.on_draw_2d)
        self.eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.eventbus.subscribe("user:mouse:release", self.on_mouse_release)
        self.eventbus.subscribe("user:mouse:drag", self.on_mouse_drag)
        self.eventbus.subscribe("user:mouse:scroll", self.on_mouse_scroll)

    async def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.ESCAPE:
            await shared.inventory_handler.remove_one_from_stack()

        x, y = shared.window.mouse_position
        slot, inventory = self._get_slot_inventory_for(x, y)

        if slot and symbol == key.Q:
            player = shared.world.get_active_player()
            dimension = shared.world.get_active_dimension()
            itemstack = slot.get_itemstack()

            if modifiers & key.MOD_SHIFT:
                dimension.spawn_itemstack_in_world(
                    itemstack.copy(), player.position, pickup_delay=10
                )
                itemstack.clean()

            else:
                dimension.spawn_itemstack_in_world(
                    itemstack.copy().set_amount(1),
                    player.position,
                    pickup_delay=10,
                )
                itemstack.add_amount(-1)

        elif slot is not None and slot.on_button_press is not None:
            px, py = inventory.get_position()

            slot.on_button_press(x - px, y - py, symbol, modifiers)

    def on_draw_2d(self):
        hovering_slot, hovering_inventory = self._get_slot_inventory_for(
            *shared.window.mouse_position
        )
        if any(
            [
                inventory.is_blocking_interactions()
                for inventory in shared.inventory_handler.open_containers
            ]
        ):
            shared.window.set_exclusive_mouse(False)
            shared.state_handler.states["minecraft:game"].parts[
                0
            ].activate_keyboard = False
        else:
            shared.state_handler.update_mouse_exclusive_state()
            shared.state_handler.states["minecraft:game"].parts[
                0
            ].activate_keyboard = True

        for inventory in shared.inventory_handler.open_containers:
            shared.rendering_helper.enableAlpha()  # make sure that it is enabled
            inventory.draw(hovering_slot=hovering_slot)

        if not shared.inventory_handler.moving_slot.get_itemstack().is_empty():
            shared.inventory_handler.moving_slot.position = shared.window.mouse_position
            shared.inventory_handler.moving_slot.draw(0, 0)
            shared.inventory_handler.moving_slot.draw_label()

        # First, render tooltip for item attached to the mouse, and than for the over the mouse is
        if (
            self.moving_itemstack is not None
            and not shared.inventory_handler.moving_slot.get_itemstack().is_empty()
        ):
            x, y = shared.window.mouse_position
            self.tool_tip_renderer.renderFor(
                shared.inventory_handler.moving_slot.get_itemstack(), (x + 32, y + 32)
            )
        elif hovering_slot is not None and not hovering_slot.get_itemstack().is_empty():
            x, y = hovering_slot.position
            ix, iy = hovering_inventory.get_position()
            self.tool_tip_renderer.renderFor(
                hovering_slot.get_itemstack(), (x + ix + 32, y + iy + 32)
            )

    def _get_slot_for(self, x: int, y: int) -> mcpython.client.gui.Slot.Slot | None:
        """
        Gets slot for position
        :param x: the x position
        :param y: the y position
        :return: the slot or None if none found
        todo: move to InventoryHandler
        """
        for inventory in itertools.chain(
            shared.inventory_handler.open_containers,
            shared.inventory_handler.always_open_containers,
        ):
            dx, dy = inventory.get_position()
            for slot in inventory.get_interaction_slots():
                sx, sy = slot.position
                sx += dx
                sy += dy
                if 0 <= x - sx <= 32 and 0 <= y - sy <= 32:
                    return slot

    def get_inventory_for(self, x: int, y: int):
        for inventory in itertools.chain(
            shared.inventory_handler.open_containers,
            shared.inventory_handler.always_open_containers,
        ):
            if inventory.is_mouse_in_range(x, y):
                return inventory

    def _get_slot_inventory_for(
        self, x: int, y: int
    ) -> typing.Tuple[mcpython.client.gui.Slot.Slot | None, typing.Any]:
        """
        Gets inventory of the slot for the position
        :param x: the x position
        :param y: the y position
        :return: the slot and the inventory or None and None if none found
        todo: move to InventoryHandler
        """
        for inventory in shared.inventory_handler.open_containers:
            dx, dy = inventory.get_position()
            for slot in inventory.get_interaction_slots():
                sx, sy = slot.position
                sx += dx
                sy += dy
                if 0 <= x - sx <= 32 and 0 <= y - sy <= 32:
                    return slot, inventory
        return None, None

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        # when no mouse interaction is active, do nothing
        if shared.window.exclusive:
            return

        self.moving_itemstack = shared.inventory_handler.moving_slot.itemstack.copy()
        moving_itemstack = shared.inventory_handler.moving_slot.itemstack

        slot: mcpython.client.gui.Slot.Slot = self._get_slot_for(x, y)

        # Check all open inventories for a handle
        for inventory in shared.inventory_handler.open_containers:
            ix, iy = inventory.get_position()

            if inventory.on_mouse_button_press(
                x - ix, y - iy, button, modifiers, moving_itemstack, slot
            ):
                return

        if slot is None:

            player = shared.world.get_active_player()
            dimension = player.dimension

            if (
                self.get_inventory_for(x, y) is None
                and shared.IS_CLIENT
                and not moving_itemstack.is_empty()
            ):
                if button == mouse.LEFT:
                    dimension.spawn_itemstack_in_world(
                        moving_itemstack.copy(), player.position, pickup_delay=10
                    )
                    moving_itemstack.clean()

                elif button == mouse.RIGHT:
                    dimension.spawn_itemstack_in_world(
                        moving_itemstack.copy().set_amount(1),
                        player.position,
                        pickup_delay=10,
                    )
                    moving_itemstack.add_amount(-1)

            return

        if slot.handle_click(button, modifiers):
            return

        if modifiers & key.MOD_SHIFT:
            if self.handle_shift_click(button, modifiers, slot, x, y):
                return

        if button == mouse.LEFT:
            if self.handle_left_click(button, modifiers, moving_itemstack, slot, x, y):
                return

        elif button == mouse.RIGHT:
            if self.handle_right_click(button, modifiers, moving_itemstack, slot, x, y):
                return

        elif button == mouse.MIDDLE:
            if self.handle_middle_click(
                button, modifiers, moving_itemstack, slot, x, y
            ):
                return

    def handle_shift_click(self, button: int, modifiers: int, slot, x: int, y: int):
        if slot.on_shift_click:
            try:
                flag = slot.on_shift_click(
                    slot, x, y, button, modifiers, shared.world.get_active_player()
                )

                # no default logic should go on
                if flag is not True:
                    return True
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                logger.print_exception(
                    "during shift-clicking {}, the function {} crashed".format(
                        slot, slot.on_shift_click
                    )
                )

        if (
            shared.inventory_handler.shift_container_handler is not None
            and shared.inventory_handler.shift_container_handler.move_to_opposite(slot)
        ):
            return True

        return False

    def handle_middle_click(
        self,
        button: int,
        modifiers: int,
        moving_itemstack: ItemStack,
        slot,
        x: int,
        y: int,
    ):
        if (
            moving_itemstack.is_empty()
            and shared.world.get_active_player().gamemode == 1
            and slot.interaction_mode[0]
        ):
            shared.inventory_handler.moving_slot.set_itemstack(
                slot.itemstack.copy().set_amount(slot.itemstack.item.STACK_SIZE)
            )
        elif shared.world.get_active_player().gamemode == 1 and slot.is_item_allowed(
            moving_itemstack
        ):
            self.mode = 3
            self.on_mouse_drag(x, y, 0, 0, button, modifiers)

        else:
            return False

        return True

    def handle_right_click(
        self,
        button: int,
        modifiers: int,
        moving_itemstack: ItemStack,
        slot,
        x: int,
        y: int,
    ):
        if moving_itemstack.is_empty() and slot.allow_half_getting:
            if not slot.interaction_mode[0]:
                return False

            amount = slot.itemstack.amount
            shared.inventory_handler.moving_slot.set_itemstack(
                slot.itemstack.copy().set_amount(amount - amount // 2)
            )
            slot.itemstack.set_amount(amount // 2)
            slot.call_update(True)

        elif slot.is_item_allowed(moving_itemstack) and (
            slot.itemstack.is_empty()
            or slot.itemstack.contains_same_resource(moving_itemstack)
        ):
            self.mode = 2
            self.on_mouse_drag(x, y, 0, 0, button, modifiers)

        else:
            return False

        return True

    def handle_left_click(
        self,
        button: int,
        modifiers: int,
        moving_itemstack: ItemStack,
        slot,
        x: int,
        y: int,
    ):
        # Is the current stack held by the player empty?
        if self.moving_itemstack.is_empty():
            if not slot.interaction_mode[0]:
                return False

            shared.inventory_handler.moving_slot.set_itemstack(slot.itemstack.copy())
            slot.clean_itemstack()
            slot.call_update(True)

        elif slot.is_item_allowed(moving_itemstack) and (
            slot.itemstack.is_empty()
            or slot.itemstack.contains_same_resource(moving_itemstack)
        ):
            self.mode = 1
            self.on_mouse_drag(x, y, 0, 0, button, modifiers)

        elif slot.interaction_mode[1]:
            stack_a = slot.get_itemstack().copy()
            slot.set_itemstack(moving_itemstack)
            shared.inventory_handler.moving_slot.set_itemstack(stack_a)

        else:
            return False

        return True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if (
            shared.window.exclusive
        ):  # when no mouse interaction is active, do nothing beside clearing the status
            self.slot_list.clear()
            self.original_amount.clear()
            self.moving_itemstack = None
            self.mode = 0
            return

        self.reorder_slot_list_stacks()

        if self.mode == 1:
            if len(self.slot_list) == 0:
                pass  # todo: drop item [see entity update]
            self.slot_list.clear()
            self.original_amount.clear()
            self.moving_itemstack = None
            self.mode = 0

        elif self.mode == 2:
            if len(self.slot_list) == 0:
                pass  # todo: drop item [see entity update]
            self.slot_list.clear()
            self.original_amount.clear()
            self.moving_itemstack = None
            self.mode = 0

        elif self.mode == 3:
            self.slot_list.clear()
            self.original_amount.clear()
            self.moving_itemstack = None
            self.mode = 0
            shared.inventory_handler.moving_slot.itemstack.clean()

    async def deactivate(self):
        await super().deactivate()

        if shared.IS_CLIENT:
            self.on_mouse_release(0, 0, 0, 0)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if shared.window.exclusive:
            return  # when no mouse interaction is active, do nothing

        slot = self._get_slot_for(x, y)
        if slot is None:
            return

        if self.mode != 0 and (
            slot.itemstack.item == self.moving_itemstack.item
            or slot.itemstack.is_empty()
        ):
            if not slot.is_item_allowed(self.moving_itemstack):
                return

            if not slot.interaction_mode[1]:
                return

            if slot not in self.slot_list:
                self.slot_list.append(slot)
                self.original_amount.append(slot.itemstack.amount)

            self.reorder_slot_list_stacks()

        elif modifiers & key.MOD_SHIFT:
            slot = self._get_slot_for(x, y)
            if slot.on_shift_click:
                try:
                    flag = slot.on_shift_click(
                        slot, x, y, button, modifiers, shared.world.get_active_player()
                    )
                    if flag is not True:
                        return  # no default logic should go on
                except:
                    logger.print_exception(
                        "during shift-clicking {}, the function {} crashed".format(
                            slot, slot.on_shift_click
                        )
                    )
            if (
                shared.inventory_handler.shift_container_handler is not None
                and shared.inventory_handler.shift_container_handler.move_to_opposite(
                    slot
                )
            ):
                return

    def reorder_slot_list_stacks(self):
        if len(self.slot_list) == 0:
            return

        if self.mode == 1:
            total = self.moving_itemstack.amount
            per_element = total // len(self.slot_list)
            overhead = total - per_element * len(self.slot_list)
            for i, slot in enumerate(self.slot_list):
                x = 0 if overhead == 0 else 1
                if overhead > 0:
                    overhead -= 1

                if slot.itemstack.is_empty():
                    slot.set_itemstack(self.moving_itemstack.copy())

                count = self.original_amount[i] + per_element + x
                off = max(0, count - self.moving_itemstack.item.STACK_SIZE)
                slot.itemstack.set_amount(count - off)
                overhead += off
                slot.call_update(True)

            shared.inventory_handler.moving_slot.itemstack.clean()

        elif self.mode == 2:
            overhead = self.moving_itemstack.amount
            for i, slot in enumerate(self.slot_list):
                if overhead > 0 and (
                    slot.get_itemstack().is_empty()
                    or slot.get_itemstack().amount
                    < slot.get_itemstack().item.STACK_SIZE
                ):
                    if slot.itemstack.is_empty():
                        slot.set_itemstack(self.moving_itemstack.copy())
                    slot.itemstack.set_amount(self.original_amount[i] + 1)
                    overhead -= 1
                    slot.call_update(True)
            shared.inventory_handler.moving_slot.itemstack.set_amount(overhead)

        elif self.mode == 3:
            for i, slot in enumerate(self.slot_list):
                if slot.itemstack.item != self.moving_itemstack.item:
                    slot.set_itemstack(self.moving_itemstack.copy())
                slot.itemstack.set_amount(slot.itemstack.item.STACK_SIZE)
                slot.call_update(True)

    def on_mouse_scroll(self, x: int, y: int, dx: int, dy: int):
        if (
            shared.window.exclusive
            or self.mode != 0
            or not shared.window.keys[key.LSHIFT]
        ):
            return  # when no mouse interaction is active, do nothing

        slot = self._get_slot_for(x, y)
        if slot is None:
            return

        if shared.inventory_handler.shift_container_handler is not None:
            if shared.window.keys[key.LSHIFT]:
                shared.inventory_handler.shift_container_handler.move_to_opposite(slot)

            else:
                shared.inventory_handler.shift_container_handler.move_to_opposite(
                    slot, count=dy
                )


inventory_part = OpenedInventoryStatePart()


class InventoryHandler:
    """
    Main class for registration of inventories

    Will handle every inventory created at any time. Will keep track of which inventories are open and to send the
        events to their event bus.

    Please do not mess around with the internal lists as they are representing the state of the inventory system.
    As such, this stuff is not API and may change at any point
    """

    def __init__(self):
        self.open_containers = []
        self.always_open_containers = []
        self.containers = []  # todo: can we make this weak?
        self.moving_slot: mcpython.client.gui.Slot.Slot = mcpython.client.gui.Slot.Slot(
            allow_player_add_to_free_place=False,
            allow_player_insert=False,
            allow_player_remove=False,
        )
        self.shift_container_handler = (
            mcpython.client.gui.ShiftContainer.ShiftContainer()
        )

    def tick(self, dt: float):
        for inventory in self.open_containers:
            inventory.tick(dt)

    def update_shift_container(self):
        for inventory in self.open_containers:
            inventory.update_shift_container()

    async def add(self, inventory):
        """
        Adds a new inventory to the internal handling system
        :param inventory: the inventory to add
        """
        if inventory in self.containers:
            return

        self.containers.append(inventory)

        if inventory.is_always_open():
            self.always_open_containers.append(inventory)
            await self.show(inventory)

    async def reload_config(self):
        await asyncio.gather(
            *[inventory.reload_config() for inventory in self.containers]
        )

    async def show(self, inventory):
        """
        Shows a inventory by adding it to the corresponding structure
        :param inventory: the inventory to show
        """
        if inventory in self.open_containers:
            return

        self.open_containers.append(inventory)
        await inventory.on_activate()
        self.update_shift_container()

        await shared.event_handler.call_async("minecraft:inventory:show", inventory)

    async def hide(self, inventory, force=False):
        """
        Hides an inventory
        :param inventory: the inventory to hide
        :param force: if force hide, skipping flag check for always active
        """
        if inventory not in self.open_containers:
            return

        if inventory in self.always_open_containers and not force:
            return

        await inventory.on_deactivate()
        self.open_containers.remove(inventory)
        self.update_shift_container()

        await shared.event_handler.call_async("minecraft:inventory:hide", inventory)

    async def remove_one_from_stack(self, is_escape=True):
        """
        Removes one inventory from stack which can be removed
        :param is_escape: if to handle like it is an escape press, so we skip containers not wanting to be closed that
            way
        :return: the inventory removed or None if no is active
        """
        stack = self.open_containers.copy()
        stack.reverse()
        for inventory in stack:
            if inventory.is_closable_by_escape() or not is_escape:
                await self.hide(inventory)
                return inventory

    def close_all_inventories(self):
        """
        Close all inventories currently open, excluding inventories marked for always being open
        """
        for inventory in self.open_containers:
            if inventory in self.always_open_containers:
                continue

            self.hide(inventory)


shared.inventory_handler = InventoryHandler()
