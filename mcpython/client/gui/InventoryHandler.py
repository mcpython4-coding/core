"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.client.gui.Inventory
import mcpython.client.state.StatePart
from pyglet.window import key, mouse
import mcpython.client.gui.Slot
import mcpython.client.gui.ShiftContainer
import mcpython.client.gui.HoveringItemBox


class OpenedInventoryStatePart(mcpython.client.state.StatePart.StatePart):
    """
    class for inventories as state
    todo: make A LOT OF THINGS public and static
    todo: move inventory interaction handling to seperated class
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
            G.inventoryhandler.remove_one_from_stack()
        x, y = G.window.mouse_position
        slot = self._get_slot_for(x, y)
        if slot is not None and slot.on_button_press is not None:
            slot.on_button_press(x, y, symbol, modifiers)

    def on_draw_2d(self):
        hoveringslot, hoveringinvenory = self._get_slot_inventory_for(
            *G.window.mouse_position
        )
        if any(
            [
                inventory.is_blocking_interactions()
                for inventory in G.inventoryhandler.opened_inventorystack
            ]
        ):
            G.window.set_exclusive_mouse(False)
            G.statehandler.states["minecraft:game"].parts[0].activate_keyboard = False
        else:
            G.statehandler.update_exclusive()
            G.statehandler.states["minecraft:game"].parts[0].activate_keyboard = True
        for inventory in G.inventoryhandler.opened_inventorystack:
            G.rendering_helper.enableAlpha()  # make sure that it is enabled
            inventory.draw(hoveringslot=hoveringslot)
        if not G.inventoryhandler.moving_slot.get_itemstack().is_empty():
            G.inventoryhandler.moving_slot.position = G.window.mouse_position
            G.inventoryhandler.moving_slot.draw(0, 0)
            G.inventoryhandler.moving_slot.draw_label()

        # First, render tooltip for item attached to the mouse, and than for the over the mouse is
        if (
            self.moving_itemstack is not None
            and not G.inventoryhandler.moving_slot.get_itemstack().is_empty()
        ):
            x, y = G.window.mouse_position
            self.tool_tip_renderer.renderFor(
                G.inventoryhandler.moving_slot.get_itemstack(), (x + 32, y + 32)
            )
        elif hoveringslot is not None and not hoveringslot.get_itemstack().is_empty():
            x, y = hoveringslot.position
            ix, iy = hoveringinvenory.get_position()
            self.tool_tip_renderer.renderFor(
                hoveringslot.get_itemstack(), (x + ix + 32, y + iy + 32)
            )

    def _get_slot_for(self, x, y) -> mcpython.client.gui.Slot.Slot:
        """
        get slot for position
        :param x: the x position
        :param y: the y position
        :return: the slot or None if none found
        todo: move to InventoryHandler
        """
        for inventory in G.inventoryhandler.opened_inventorystack:
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
        for inventory in G.inventoryhandler.opened_inventorystack:
            dx, dy = inventory.get_position()
            for slot in inventory.get_interaction_slots():
                sx, sy = slot.position
                sx += dx
                sy += dy
                if 0 <= x - sx <= 32 and 0 <= y - sy <= 32:
                    return slot, inventory
        return None, None

    def on_mouse_press(self, x, y, button, modifiers):
        if G.window.exclusive:
            return  # when no mouse interaction is active, do nothing
        slot: mcpython.client.gui.Slot.Slot = self._get_slot_for(x, y)
        if slot is None:
            return
        self.moving_itemstack = G.inventoryhandler.moving_slot.itemstack.copy()
        moving_itemstack = G.inventoryhandler.moving_slot.itemstack
        if modifiers & key.MOD_SHIFT:
            if slot.on_shift_click:
                try:
                    flag = slot.on_shift_click(
                        slot, x, y, button, modifiers, G.world.get_active_player()
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
                G.inventoryhandler.shift_container is not None
                and G.inventoryhandler.shift_container.move_to_opposite(slot)
            ):
                return
        if button == mouse.LEFT:
            if self.moving_itemstack.is_empty():
                if not slot.interaction_mode[0]:
                    return
                G.inventoryhandler.moving_slot.set_itemstack(slot.itemstack.copy())
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
            else:
                self.mode = 1
                self.on_mouse_drag(x, y, 0, 0, button, modifiers)
        elif button == mouse.RIGHT:
            if moving_itemstack.is_empty() and slot.allow_half_getting:
                if not slot.interaction_mode[0]:
                    return
                amount = slot.itemstack.amount
                G.inventoryhandler.moving_slot.set_itemstack(
                    slot.itemstack.copy().set_amount(amount - amount // 2)
                )
                slot.itemstack.set_amount(amount // 2)
                slot.call_update(True)
            else:
                self.mode = 2
                self.on_mouse_drag(x, y, 0, 0, button, modifiers)
        elif button == mouse.MIDDLE:
            if (
                moving_itemstack.is_empty()
                and G.world.get_active_player().gamemode == 1
            ):
                G.inventoryhandler.moving_slot.set_itemstack(
                    slot.itemstack.copy().set_amount(slot.itemstack.item.STACK_SIZE)
                )
            elif G.world.get_active_player().gamemode == 1:
                self.mode = 3
                self.on_mouse_drag(x, y, 0, 0, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if (
            G.window.exclusive
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
            G.inventoryhandler.moving_slot.itemstack.clean()

    def deactivate(self):
        for statepart in self.parts:
            statepart.deactivate()
        self.on_mouse_release(0, 0, 0, 0)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if G.window.exclusive:
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
                        slot, x, y, button, modifiers, G.world.get_active_player()
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
                G.inventoryhandler.shift_container is not None
                and G.inventoryhandler.shift_container.move_to_opposite(slot)
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
            G.inventoryhandler.moving_slot.itemstack.clean()
        elif self.mode == 2:
            overhead = self.moving_itemstack.amount
            for i, slot in enumerate(self.slot_list):
                if overhead > 0:
                    if slot.itemstack.is_empty():
                        slot.set_itemstack(self.moving_itemstack.copy())
                    slot.itemstack.set_amount(self.original_amount[i] + 1)
                    overhead -= 1
                    slot.call_update(True)
            G.inventoryhandler.moving_slot.itemstack.set_amount(overhead)
        elif self.mode == 3:
            for i, slot in enumerate(self.slot_list):
                if slot.itemstack.item != self.moving_itemstack.item:
                    slot.set_itemstack(self.moving_itemstack.copy())
                slot.itemstack.set_amount(slot.itemstack.item.STACK_SIZE)
                slot.call_update(True)

    def on_mouse_scroll(self, x, y, dx, dy):
        if G.window.exclusive:
            return  # when no mouse interaction is active, do nothing
        slot = self._get_slot_for(x, y)
        if slot is None:
            return
        if self.mode != 0:
            return
        if G.inventoryhandler.shift_container is not None:
            if G.window.keys[key.LSHIFT]:
                G.inventoryhandler.shift_container.move_to_opposite(slot)
            else:
                G.inventoryhandler.shift_container.move_to_opposite(slot, count=1)


inventory_part = OpenedInventoryStatePart()


class InventoryHandler:
    """
    main class for registration of inventories
    Will handle every inventory created at any time. Will keep track of which inventories are open and to send the
        events to their event bus.
    Please do not mess around with the internal lists as they are representing the state of the inventory system.
    """

    def __init__(self):
        self.opened_inventorystack = []
        self.alwaysopened = []
        self.inventorys = []
        self.moving_slot: mcpython.client.gui.Slot.Slot = mcpython.client.gui.Slot.Slot(
            allow_player_add_to_free_place=False,
            allow_player_insert=False,
            allow_player_remove=False,
        )
        self.shift_container = mcpython.client.gui.ShiftContainer.ShiftContainer()

    def update_shift_container(self):
        for inventory in self.opened_inventorystack:
            inventory.update_shift_container()

    def add(self, inventory):
        """
        add an new inventory
        :param inventory: the inventory to add
        """
        if inventory in self.inventorys:
            return
        self.inventorys.append(inventory)
        if inventory.is_always_open():
            self.alwaysopened.append(inventory)
            self.show(inventory)

    def reload_config(self):
        [inventory.reload_config() for inventory in self.inventorys]

    def show(self, inventory):
        """
        show an inventory
        :param inventory: the inventory to show
        """
        if inventory in self.opened_inventorystack:
            return
        self.opened_inventorystack.append(inventory)
        inventory.on_activate()
        self.update_shift_container()
        G.eventhandler.call("inventory:show", inventory)
        G.eventhandler.call(
            "inventory:show:{}".format(inventory.__class__.__name__), inventory
        )

    def hide(self, inventory):
        """
        hide an inventory
        :param inventory: the inventory to hide
        """
        if inventory not in self.opened_inventorystack:
            return
        if inventory in self.alwaysopened:
            return
        inventory.on_deactivate()
        self.opened_inventorystack.remove(inventory)
        self.update_shift_container()
        G.eventhandler.call("inventory:hide", inventory)
        G.eventhandler.call(
            "inventory:hide:{}".format(inventory.__class__.__name__), inventory
        )

    def remove_one_from_stack(self):
        """
        removes one inventory from stack
        :return: the inventory removed or None if no is active
        """
        stack = self.opened_inventorystack.copy()
        stack.reverse()
        for inventory in stack:
            if inventory.is_closable_by_escape():
                self.hide(inventory)
                return inventory

    def close_all_inventories(self):
        """
        close all inventories
        """
        for inventory in self.opened_inventorystack:
            if inventory in self.alwaysopened:
                continue
            self.hide(inventory)


G.inventoryhandler = InventoryHandler()