"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import gui.Inventory
import gui.Slot
import gui.ItemStack
import crafting.CraftingHandler
import crafting.FurnaceCrafting
import event.EventHandler
import pyglet
import time
import logger
import ResourceLocator


arrow = ResourceLocator.read("build/texture/gui/furnace_arrow.png", "pyglet")
fire = ResourceLocator.read("build/texture/gui/furnace_fire.png", "pyglet")


class InventoryFurnace(gui.Inventory.Inventory):
    """
    inventory class for the furnace
    """

    def __init__(self, block, types):
        super().__init__()
        self.block = block
        self.fuel_left = 0
        self.fuel_max = 0
        self.xp_stored = 0
        self.smelt_start = None
        self.old_item_name = None
        self.recipe = None
        self.progress = 0
        self.types = types

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/blockinventoryfurnace.json"

    def reset(self):
        self.block.active = False
        self.block.face_state.update()
        self.smelt_start = None
        self.recipe = None
        self.old_item_name = None

    def update_status(self):
        if any([self.slots[0].itemstack.get_item_name() in G.craftinghandler.furnace_recipes[x] for x in self.types]):
            if self.fuel_left == 0:
                if self.slots[1].itemstack.is_empty():
                    self.reset()
                    return
                # consume one fuel
                try:
                    fuel = self.slots[1].itemstack.item.FUEL
                    self.fuel_max = fuel
                    self.fuel_left += fuel
                except AttributeError:
                    logger.println("[FUEL][WARNING] item '{}' was marked as fuel but did NOT have FUEL-attribute".
                                   format(self.slots[1].itemstack.get_item_name()))
                    self.reset()
                    return
                self.slots[1].itemstack.add_amount(-1)
            if self.slots[0].itemstack.get_item_name() == self.old_item_name: return
            self.old_item_name = self.slots[0].itemstack.get_item_name()
            self.smelt_start = time.time()
            for x in self.types:
                if self.old_item_name in G.craftinghandler.furnace_recipes[x]:
                    recipe = G.craftinghandler.furnace_recipes[x][self.old_item_name]
                    break
            else:
                logger.println("[ERROR] no recipe found")
                self.reset()
                return
            if self.slots[2].itemstack.get_item_name() is not None and (
                    self.slots[2].itemstack.get_item_name() != recipe.output or
                    self.slots[2].itemstack.amount >= self.slots[2].itemstack.item.STACK_SIZE):
                if not self.slots[2].itemstack.is_empty():
                    print(self.slots[2].itemstack.get_item_name() != recipe.output,
                          self.slots[2].itemstack.amount, self.slots[2].itemstack.item.STACK_SIZE)
                self.reset()
                return
            self.recipe: crafting.FurnaceCrafting.FurnesRecipe = recipe
            self.block.active = True
            self.block.face_state.update()
        else:
            self.reset()

    def create_slots(self) -> list:
        # 36 slots of main, 1 input, 1 fuel and 1 output
        slots = [gui.Slot.Slot(on_update=self.on_input_update, on_shift_click=self.on_shift),
                 gui.Slot.Slot(allowed_item_tags=["#minecraft:furnace_fuel"], on_update=self.on_fuel_slot_update,
                               on_shift_click=self.on_shift),
                 gui.Slot.Slot(on_update=self.on_output_update, on_shift_click=self.on_shift)]
        return slots

    @staticmethod
    def on_shift(slot, x, y, button, mod):
        slot_copy = slot.itemstack.copy()
        if G.world.get_active_player().pick_up(slot_copy):
            slot.itemstack.clean()  # if we successfully added the itemstack, we have to clear it
        else:
            slot.itemstack.set_amount(slot_copy.itemstack.itemstack)

    def on_input_update(self, player=False):
        if self.slots[0].itemstack.is_empty(): self.reset()
        else: self.update_status()

    def on_fuel_slot_update(self, player=False):
        self.update_status()

    def on_output_update(self, player=False):
        self.update_status()

    def on_activate(self):
        super().on_activate()
        try:
            event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("user:keyboard:press", self.on_key_press)
            event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("gameloop:tick:end", self.on_tick)
        except ValueError:
            pass
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("user:keyboard:press", self.on_key_press)
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("gameloop:tick:end", self.on_tick)

    def on_deactivate(self):
        super().on_deactivate()
        G.world.get_active_player().reset_moving_slot()
        event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("user:keyboard:press", self.on_key_press)
        event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe("gameloop:tick:end", self.on_tick)

    def draw(self, hoveringslot=None):
        """
        draws the inventory
        """
        self.on_draw_background()
        x, y = self._get_position()
        if self.bgsprite:
            self.bgsprite.position = (x, y)
            self.bgsprite.draw()
        self.on_draw_over_backgroundimage()

        # draw arrow
        if self.recipe and self.progress > 0:
            try:
                arrow.get_region(0, 0, round(48 * self.progress), 33).blit(x+159, y+229)
            except ZeroDivisionError:
                pass

        # draw fire
        if self.fuel_max > 0:
            try:
                fire.get_region(0, 0, 28, round(28 * (self.fuel_left / self.fuel_max))).blit(x+112, y+229)
            except ZeroDivisionError:
                pass

        for slot in G.world.get_active_player().inventories["main"].slots[:36] + self.slots:
            slot.draw(x, y, hovering=slot == hoveringslot)
        self.on_draw_over_image()
        for slot in G.world.get_active_player().inventories["main"].slots[:36] + self.slots:
            slot.draw_lable(x, y)
        self.on_draw_overlay()

    def get_interaction_slots(self):
        return G.world.get_active_player().inventories["main"].slots[:36] + self.slots

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E: G.inventoryhandler.hide(self)

    def on_tick(self, dt):
        if self.fuel_left > 0:
            self.fuel_left = max(self.fuel_left - round(dt*100)/100, 0)
        if self.recipe is not None:
            if self.fuel_left == 0:
                if self.progress > 0.99:
                    self.finish()
                else:
                    self.update_status()
                return
            elapsed_time = time.time() - self.smelt_start
            self.progress = min(elapsed_time / self.recipe.time, 1)
            if self.progress >= 1:
                self.finish()
        elif not self.slots[0].itemstack.is_empty() and (not self.slots[1].itemstack.is_empty() or self.fuel_left > 0):
            self.update_status()

    def finish(self):
        if self.slots[2].itemstack.is_empty():
            self.slots[2].itemstack = gui.ItemStack.ItemStack(self.recipe.output)
        else:
            if self.slots[2].itemstack.item.STACK_SIZE > self.slots[2].itemstack.amount:
                self.slots[2].itemstack.add_amount(1)
        self.slots[0].itemstack.add_amount(-1)
        try:
            G.world.get_active_player().add_xp(self.recipe.xp)
        except AttributeError:
            pass
        self.smelt_start = time.time()
        self.update_status()

    def load(self, data: dict) -> bool:
        self.fuel_left = data.setdefault("fuel", 0)
        self.fuel_max = data.setdefault("max fuel", 0)
        self.xp_stored = data.setdefault("xp", 0)
        self.progress = data.setdefault("progress", 0)
        self.update_status()
        return True

    def save(self):
        return {"fuel": self.fuel_left, "max fuel": self.fuel_max, "xp": self.xp_stored, "progress": self.progress}

