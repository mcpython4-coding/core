"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Block
from pyglet.window import mouse, key
import item.ItemTool
import util.enums
import pyglet
import util.enums
import gui.InventoryBarrel


@G.registry
class BlockBarrel(Block.Block):
    NAME = "minecraft:barrel"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.facing = "up"
        self.opened = False
        self.inventory = gui.InventoryBarrel.InventoryBarrel(self)
        if self.set_to is not None:
            dx, dy, dz = tuple([self.position[i] - self.set_to[i] for i in range(3)])
            if dx > 0:   self.facing = "west"
            elif dz > 0: self.facing = "north"
            elif dx < 0: self.facing = "east"
            elif dz < 0: self.facing = "south"
            elif dy > 0: self.facing = "down"
            elif dy < 0: self.facing = "up"

    def on_player_interact(self, player, itemstack, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    HARDNESS = 2.5
    BEST_TOOLS_TO_BREAK = [item.ItemTool.ToolType.AXE]

    def get_provided_slots(self, side): return self.inventory.slots

    def set_model_state(self, state: dict):
        if "side" in state:
            face = state["side"]
            if type(face) == str:
                self.front_side = util.enums.EnumSide[state["side"]]
            else:
                self.front_side = face

    def get_model_state(self) -> dict:
        return {"facing": self.facing, "open": str(self.opened).lower()}

    @staticmethod
    def get_all_model_states() -> list:
        facing = [{"facing": "north"}, {"facing": "east"}, {"facing": "south"},
                  {"facing": "west"}, {"facing": "up"}, {"facing": "down"}]
        return [{"open": "false", **e} for e in facing] + [{"open": "true", **e} for e in facing]

    @classmethod
    def set_block_data(cls, iteminst, block):
        if hasattr(iteminst, "inventory"):
            block.inventory = iteminst.inventory.copy()

    def on_request_item_for_block(self, itemstack):
        if G.window.keys[pyglet.window.key.LCTRL] and G.world.get_active_player().gamemode == 1 and G.window.mouse_pressing[
                pyglet.window.mouse.MIDDLE]:
            itemstack.item.inventory = self.inventory.copy()

    def on_remove(self):
        if not G.world.gamerulehandler.table["doTileDrops"].status.status: return
        for slot in self.inventory.slots:
            G.world.get_active_player().pick_up(slot.itemstack.copy())
            slot.itemstack.clean()
        G.inventoryhandler.hide(self.inventory)
        del self.inventory

    @classmethod
    def modify_block_item(cls, itemfactory):
        itemfactory.setFuelLevel(15)

