"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import globals as G
import gui.Inventory
import state.StatePart
import state.StatePartGame
from pyglet.window import key


class OpenedInventoryStatePart(state.StatePart.StatePart):
    def __init__(self):
        self.event_functions = [("user:keyboard:press", self.on_key_press),
                                ("render:draw:2d", self.on_draw_2d)]

    def activate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.activate_to_callback(eventname, function)

    def deactivate(self):
        for eventname, function in self.event_functions:
            G.eventhandler.deactivate_from_callback(eventname, function)

    def get_event_functions(self) -> list:
        return [(self.on_key_press, "user:keyboard:press"),
                (self.on_draw_2d, "render:draw:2d")]

    @G.eventhandler("user:keyboard:press", callactive=False)
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.inventoryhandler.remove_one_from_stack()

    @G.eventhandler("render:draw:2d", callactive=False)
    def on_draw_2d(self):
        if any([inventory.is_blocking_interactions() for inventory in G.inventoryhandler.opened_inventorystack]):
            G.window.set_exclusive_mouse(False)
        else:
            G.statehandler.update_exclusive()
        for inventory in G.inventoryhandler.opened_inventorystack:
            inventory.draw()


class InventoryHandler:
    def __init__(self):
        self.opened_inventorystack = []
        self.alwaysopened = []
        self.inventorys = []

    def add(self, inventory):
        if inventory in self.inventorys: return
        self.inventorys.append(inventory)
        if inventory.is_always_open():
            self.alwaysopened.append(inventory)
            self.show(inventory)

    def show(self, inventory):
        if inventory in self.opened_inventorystack: return
        self.opened_inventorystack.append(inventory)
        inventory.on_activate()

    def hide(self, inventory):
        if inventory not in self.opened_inventorystack: return
        if inventory in self.alwaysopened: return
        inventory.on_deactivate()
        self.opened_inventorystack.remove(inventory)

    def remove_one_from_stack(self):
        stack = self.opened_inventorystack
        stack.reverse()
        for inventory in stack:
            if inventory.is_closable_by_escape():
                self.hide(inventory)
                return

    def close_all_inventorys(self):
        for inventory in self.opened_inventorystack:
            self.hide(inventory)


G.inventoryhandler = InventoryHandler()


def load():
    pass

