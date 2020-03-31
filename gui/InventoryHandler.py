"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import gui.Inventory
import state.StatePart
import state.StatePartGame
from pyglet.window import key, mouse
import gui.Slot
import logger


class OpenedInventoryStatePart(state.StatePart.StatePart):
    """
    class for inventories as state
    todo: make A LOT OF THINGS public and static
    """

    def __init__(self):
        super().__init__()

        self.active = False

    def bind_to_eventbus(self):
        self.master[0].eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.master[0].eventbus.subscribe("render:draw:2d", self.on_draw_2d)
        self.master[0].eventbus.subscribe("user:mouse:press", self.on_mouse_press)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.inventoryhandler.remove_one_from_stack()
        x, y = G.window.mouse_position
        slot = self._get_slot_for(x, y)
        if slot is not None and slot.on_button_press is not None:
            slot.on_button_press(x, y, symbol, modifiers)

    def on_draw_2d(self):
        hoveringslot = self._get_slot_for(*G.window.mouse_position)
        if any([inventory.is_blocking_interactions() for inventory in G.inventoryhandler.opened_inventorystack]):
            G.window.set_exclusive_mouse(False)
            G.statehandler.states["minecraft:game"].parts[0].activate_keyboard = False
        else:
            G.statehandler.update_exclusive()
            G.statehandler.states["minecraft:game"].parts[0].activate_keyboard = True
        for inventory in G.inventoryhandler.opened_inventorystack:
            inventory.draw(hoveringslot=hoveringslot)
        if G.inventoryhandler.moving_slot.get_itemstack().item:
            G.inventoryhandler.moving_slot.position = G.window.mouse_position
            G.inventoryhandler.moving_slot.draw(0, 0)
            G.inventoryhandler.moving_slot.draw_lable(0, 0)

    def _get_slot_for(self, x, y) -> gui.Slot.Slot or None:
        """
        get slot for position
        :param x: the x position
        :param y: the y position
        :return: the slot or None if none found
        """
        for inventory in G.inventoryhandler.opened_inventorystack:
            dx, dy = inventory._get_position()
            for slot in inventory.get_interaction_slots():
                sx, sy = slot.position
                sx += dx
                sy += dy
                if 0 <= x - sx <= 32 and 0 <= y - sy <= 32:
                    return slot
        return None

    def handle_left_click(self, x, y, slot, modifiers):
        moving_slot = G.inventoryhandler.moving_slot
        if slot and (slot.interaction_mode[0] or not slot.get_itemstack().item) and (slot.interaction_mode[1] or not
                moving_slot.get_itemstack().item):
            if slot.get_itemstack().get_item_name() == moving_slot.get_itemstack().get_item_name() and \
                    slot.get_itemstack().get_item_name() is not None:
                eamount = slot.get_itemstack().amount
                ramount = moving_slot.get_itemstack().amount
                mstack = slot.get_itemstack().item.STACK_SIZE
                if eamount == mstack: return
                possible = mstack - eamount
                if possible > ramount:
                    possible = ramount
                slot.get_itemstack().add_amount(possible)
                slot.call_update(player=True)
                moving_slot.get_itemstack().add_amount(-possible)
                if moving_slot.get_itemstack().amount <= 0:
                    moving_slot.get_itemstack().clean()
            else:
                flag = slot.can_set_item(moving_slot.get_itemstack())
                if flag:
                    stack, mstack = slot.get_itemstack(), moving_slot.get_itemstack()
                    moving_slot.set_itemstack(stack)
                    slot.set_itemstack(mstack, player=True)
        else:
            # todo: threw the itemstack [see entity update for info]
            pass

    def handle_right_click(self, x, y, slot, modifiers):
        moving_slot = G.inventoryhandler.moving_slot
        if slot:
            if not slot.get_itemstack().item:
                if slot.interaction_mode[1] and slot.can_set_item(moving_slot.get_itemstack()):
                    slot.set_itemstack(moving_slot.get_itemstack().copy().set_amount(1), player=True)
                    moving_slot.get_itemstack().add_amount(-1)
            elif not moving_slot.get_itemstack().item and slot.allow_half_getting:
                if slot.interaction_mode[0]:
                    moving_slot.set_itemstack(slot.get_itemstack().copy())
                    slot.get_itemstack().amount //= 2
                    moving_slot.get_itemstack().set_amount(
                        abs(moving_slot.get_itemstack().amount - slot.get_itemstack().amount))
                    if slot.get_itemstack().amount == 0:
                        slot.get_itemstack().clean()
                    if moving_slot.get_itemstack().amount == 0:
                        moving_slot.get_itemstack().clean()
                    slot.call_update(player=True)
            elif not slot.get_itemstack().is_empty() and slot.get_itemstack().get_item_name() == moving_slot.get_itemstack(). \
                    get_item_name() and slot.get_itemstack().amount < slot.get_itemstack().item.STACK_SIZE:
                if slot.interaction_mode[1]:
                    slot.get_itemstack().add_amount(1)
                    moving_slot.get_itemstack().add_amount(-1)
                    slot.call_update(player=True)
        else:
            # todo: threw one item [see entity update for info]
            pass

    def handle_middle_click(self, x, y, slot, modifiers):
        moving_slot = G.inventoryhandler.moving_slot
        if G.world.get_active_player().gamemode == 1 and slot and slot.get_itemstack().get_item_name() and not \
                moving_slot.get_itemstack().get_item_name():
            moving_slot.set_itemstack(slot.get_itemstack().copy())
            moving_slot.get_itemstack().set_amount(moving_slot.get_itemstack().item.STACK_SIZE)

    def on_mouse_press(self, x, y, button, modifiers):
        if G.window.exclusive: return  # when no mouse interaction is active, do nothing
        slot: gui.Slot.Slot = self._get_slot_for(x, y)
        moving_slot: gui.Slot.Slot = G.inventoryhandler.moving_slot
        if modifiers & key.MOD_SHIFT and slot.on_shift_click:
            try:
                flag = slot.on_shift_click(slot, x, y, button, modifiers)
            except:
                logger.println("error during executing function {}".format(slot.on_shift_click))
                raise
            if flag is True: return
        if button == mouse.LEFT: self.handle_left_click(x, y, slot, modifiers)
        elif button == mouse.RIGHT: self.handle_right_click(x, y, slot, modifiers)
        elif button == mouse.MIDDLE: self.handle_middle_click(x, y, slot, modifiers)
        if moving_slot.get_itemstack().amount == 0:
            moving_slot.get_itemstack().clean()


inventory_part = OpenedInventoryStatePart()


class InventoryHandler:
    """
    main class for registrating inventories
    """

    def __init__(self):
        self.opened_inventorystack = []
        self.alwaysopened = []
        self.inventorys = []
        self.moving_slot: gui.Slot.Slot = gui.Slot.Slot(allow_player_add_to_free_place=False, allow_player_insert=False,
                                                        allow_player_remove=False)

    def add(self, inventory):
        """
        add an new inventory
        :param inventory: the inventory to add
        """
        if inventory in self.inventorys: return
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
        if inventory in self.opened_inventorystack: return
        self.opened_inventorystack.append(inventory)
        inventory.on_activate()
        G.eventhandler.call("inventory:show", inventory)

    def hide(self, inventory):
        """
        hide an inventory
        :param inventory: the inventory to hide
        """
        if inventory not in self.opened_inventorystack: return
        if inventory in self.alwaysopened: return
        inventory.on_deactivate()
        self.opened_inventorystack.remove(inventory)
        G.eventhandler.call("inventory:hide", inventory)

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
            if inventory in self.alwaysopened: continue
            self.hide(inventory)


G.inventoryhandler = InventoryHandler()

