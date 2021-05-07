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
import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.HoveringItemBox
import mcpython.client.gui.ShiftContainer
import mcpython.client.gui.Slot
import mcpython.client.state.StatePart
from mcpython import logger, shared
from pyglet.window import key, mouse


class OpenedInventoryStatePart(mcpython.client.state.StatePart.StatePart):
    """
    class for inventories as state
    todo: make A LOT OF THINGS public and static
    todo: move inventory interaction handling to separated class
    """

    def __init__(self):
        super().__init__()
        self.active = False
        self.slot_list = []
        self.moving_itemstack = None
        self.mode = 0  # possible: 0 - None, 1: equal on all slots, 2: on every slot one more, 3: fill up slots
        self.original_amount = []
        self.tool_tip_renderer = (
            mcpython.client.gui.HoveringItemBox.HoveringItemBoxProvider()
        )

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)
        self.master[0].eventbus.subscribe("user:mouse:release", self.on_mouse_release)
        self.master[0].eventbus.subscribe("user:mouse:drag", self.on_mouse_drag)
        self.master[0].eventbus.subscribe("user:mouse:scroll", self.on_mouse_scroll)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            shared.inventory_handler.remove_one_from_stack()
        x, y = shared.window.mouse_position
        slot = self._get_slot_for(x, y)
        if slot is not None and slot.on_button_press is not None:
            slot.on_button_press(x, y, symbol, modifiers)

    def on_draw_2d(self):
        hovering_slot, hovering_inventory = self._get_slot_inventory_for(
            *shared.window.mouse_position
        )
        if any(
            [
                inventory.is_blocking_interactions()
                for inventory in shared.inventory_handler.opened_inventory_stack
            ]
        ):
            shared.window.set_exclusive_mouse(False)
            shared.state_handler.states["minecraft:game"].parts[
                0
            ].activate_keyboard = False
        else:
            shared.state_handler.update_exclusive()
            shared.state_handler.states["minecraft:game"].parts[
                0
            ].activate_keyboard = True
        for inventory in shared.inventory_handler.opened_inventory_stack:
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

    def _get_slot_for(self, x, y) -> mcpython.client.gui.Slot.Slot:
        """
        get slot for position
        :param x: the x position
        :param y: the y position
        :return: the slot or None if none found
        todo: move to InventoryHandler
        """
        for inventory in shared.inventory_handler.opened_inventory_stack:
            dx, dy = inventory.get_position()
            for slot in inventory.get_interaction_slots():
                sx, sy = slot.position
                sx += dx
                sy += dy
                if 0 <= x - sx <= 32 and 0 <= y - sy <= 32:
                    return slot

    def _get_slot_inventory_for(self, x, y):
        """
        get slot for position
        :param x: the x position
        :param y: the y position
        :return: the slot and the inventory or None and None if none found
        todo: move to InventoryHandler
        """
        for inventory in shared.inventory_handler.opened_inventory_stack:
            dx, dy = inventory.get_position()
            for slot in inventory.get_interaction_slots():
                sx, sy = slot.position
                sx += dx
                sy += dy
                if 0 <= x - sx <= 32 and 0 <= y - sy <= 32:
                    return slot, inventory
        return None, None

    def on_mouse_press(self, x, y, button, modifiers):
        if shared.window.exclusive:
            return  # when no mouse interaction is active, do nothing
        slot: mcpython.client.gui.Slot.Slot = self._get_slot_for(x, y)
        if slot is None:
            return
        self.moving_itemstack = shared.inventory_handler.moving_slot.itemstack.copy()
        moving_itemstack = shared.inventory_handler.moving_slot.itemstack
        if modifiers & key.MOD_SHIFT:
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
                shared.inventory_handler.shift_container is not None
                and shared.inventory_handler.shift_container.move_to_opposite(slot)
            ):
                return
        if button == mouse.LEFT:
            if self.moving_itemstack.is_empty():
                if not slot.interaction_mode[0]:
                    return
                shared.inventory_handler.moving_slot.set_itemstack(
                    slot.itemstack.copy()
                )
                slot.itemstack.clean()
                slot.call_update(True)
            elif slot.interaction_mode[1] and slot.itemstack == moving_itemstack:
                target = min(
                    slot.itemstack.item.STACK_SIZE,
                    slot.itemstack.amount + moving_itemstack.amount,
                )
                moving_itemstack.set_amount(
                    moving_itemstack.amount - (target - slot.itemstack.amount)
                )
                slot.itemstack.set_amount(target)
                slot.call_update(True)
            elif slot.can_set_item(moving_itemstack):
                self.mode = 1
                self.on_mouse_drag(x, y, 0, 0, button, modifiers)
        elif button == mouse.RIGHT:
            if moving_itemstack.is_empty() and slot.allow_half_getting:
                if not slot.interaction_mode[0]:
                    return
                amount = slot.itemstack.amount
                shared.inventory_handler.moving_slot.set_itemstack(
                    slot.itemstack.copy().set_amount(amount - amount // 2)
                )
                slot.itemstack.set_amount(amount // 2)
                slot.call_update(True)
            elif slot.can_set_item(moving_itemstack):
                self.mode = 2
                self.on_mouse_drag(x, y, 0, 0, button, modifiers)
        elif button == mouse.MIDDLE:
            if (
                moving_itemstack.is_empty()
                and shared.world.get_active_player().gamemode == 1
            ):
                shared.inventory_handler.moving_slot.set_itemstack(
                    slot.itemstack.copy().set_amount(slot.itemstack.item.STACK_SIZE)
                )
            elif shared.world.get_active_player().gamemode == 1 and slot.can_set_item(
                moving_itemstack
            ):
                self.mode = 3
                self.on_mouse_drag(x, y, 0, 0, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
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

    def deactivate(self):
        for statepart in self.parts:
            statepart.deactivate()
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
            if not slot.can_set_item(self.moving_itemstack):
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
                shared.inventory_handler.shift_container is not None
                and shared.inventory_handler.shift_container.move_to_opposite(slot)
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
                slot.itemstack.set_amount(self.original_amount[i] + per_element + x)
                slot.call_update(True)
            shared.inventory_handler.moving_slot.itemstack.clean()
        elif self.mode == 2:
            overhead = self.moving_itemstack.amount
            for i, slot in enumerate(self.slot_list):
                if overhead > 0:
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

    def on_mouse_scroll(self, x, y, dx, dy):
        if shared.window.exclusive:
            return  # when no mouse interaction is active, do nothing
        slot = self._get_slot_for(x, y)
        if slot is None:
            return
        if self.mode != 0:
            return
        if shared.inventory_handler.shift_container is not None:
            if shared.window.keys[key.LSHIFT]:
                shared.inventory_handler.shift_container.move_to_opposite(slot)
            else:
                shared.inventory_handler.shift_container.move_to_opposite(slot, count=1)


inventory_part = OpenedInventoryStatePart()


class InventoryHandler:
    """
    main class for registration of inventories
    Will handle every inventory created at any time. Will keep track of which inventories are open and to send the
        events to their event bus.
    Please do not mess around with the internal lists as they are representing the state of the inventory system.
    """

    def __init__(self):
        self.opened_inventory_stack = []
        self.always_opened = []
        self.inventories = []
        self.moving_slot: mcpython.client.gui.Slot.Slot = mcpython.client.gui.Slot.Slot(
            allow_player_add_to_free_place=False,
            allow_player_insert=False,
            allow_player_remove=False,
        )
        self.shift_container = mcpython.client.gui.ShiftContainer.ShiftContainer()

    def tick(self, dt: float):
        for inventory in self.opened_inventory_stack:
            inventory.tick(dt)

    def update_shift_container(self):
        for inventory in self.opened_inventory_stack:
            inventory.update_shift_container()

    def add(self, inventory):
        """
        add an new inventory
        :param inventory: the inventory to add
        """
        if inventory in self.inventories:
            return
        self.inventories.append(inventory)
        if inventory.is_always_open():
            self.always_opened.append(inventory)
            self.show(inventory)

    def reload_config(self):
        [inventory.reload_config() for inventory in self.inventories]

    def show(self, inventory):
        """
        show an inventory
        :param inventory: the inventory to show
        """
        if inventory in self.opened_inventory_stack:
            return
        self.opened_inventory_stack.append(inventory)
        inventory.on_activate()
        self.update_shift_container()
        shared.event_handler.call("inventory:show", inventory)
        shared.event_handler.call(
            "inventory:show:{}".format(inventory.__class__.__name__), inventory
        )

    def hide(self, inventory):
        """
        hide an inventory
        :param inventory: the inventory to hide
        """
        if inventory not in self.opened_inventory_stack:
            return
        if inventory in self.always_opened:
            return
        inventory.on_deactivate()
        self.opened_inventory_stack.remove(inventory)
        self.update_shift_container()
        shared.event_handler.call("inventory:hide", inventory)
        shared.event_handler.call(
            "inventory:hide:{}".format(inventory.__class__.__name__), inventory
        )

    def remove_one_from_stack(self):
        """
        removes one inventory from stack
        :return: the inventory removed or None if no is active
        """
        stack = self.opened_inventory_stack.copy()
        stack.reverse()
        for inventory in stack:
            if inventory.is_closable_by_escape():
                self.hide(inventory)
                return inventory

    def close_all_inventories(self):
        """
        close all inventories
        """
        for inventory in self.opened_inventory_stack:
            if inventory in self.always_opened:
                continue
            self.hide(inventory)


shared.inventory_handler = InventoryHandler()
