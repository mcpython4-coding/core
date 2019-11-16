"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
from . import Block
from pyglet.window import mouse, key
import item.ItemTool
import util.enums
import block.BoundingBox
from datetime import datetime
import pyglet
import util.enums


BBOX = block.BoundingBox.BoundingBox((14/16, 14/16, 14/16), (1/16, 1/16, 1/16))


@G.registry
class BlockChest(Block.Block):
    now = datetime.now()
    is_christmas = 24 <= now.day <= 26 and now.month == 12

    def on_create(self):
        self.front_side = util.enums.EnumSide.N
        if self.real_hit:
            dx, dz = self.real_hit[0] - self.position[0], self.real_hit[1] - self.position[1]
            if dx > 0 and abs(dx) > abs(dz):
                self.front_side = util.enums.EnumSide.N
            elif dx < 0 and abs(dx) > abs(dz):
                self.front_side = util.enums.EnumSide.S
            elif dz > 0 and abs(dx) < abs(dz):
                self.front_side = util.enums.EnumSide.E
            elif dz < 0 and abs(dx) < abs(dz):
                self.front_side = util.enums.EnumSide.W
        import gui.InventoryChest
        self.inventory = gui.InventoryChest.InventoryChest()

    @staticmethod
    def get_name() -> str:
        return "minecraft:chest"

    def can_open_inventory(self) -> bool:
        x, y, z = self.position
        blockinst = G.world.get_active_dimension().get_block((x, y+1, z))
        return blockinst is None or not blockinst.is_solid_side(util.enums.EnumSide.DOWN)

    def on_player_interact(self, itemstack, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT and self.can_open_inventory():
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    def get_hardness(self):
        return 2.5

    def get_minimum_tool_level(self):
        return 0

    def get_best_tools(self):
        return [item.ItemTool.ToolType.AXE]

    def get_provided_slots(self, side): return self.inventory.slots

    def set_model_state(self, state: dict):
        if "side" in state:
            self.front_side = util.enums.EnumSide[state["side"]]

    def get_model_state(self) -> dict:
        return {"side": self.front_side.name, "type": "normal" if not self.is_christmas else "christmas"}

    @staticmethod
    def get_all_model_states() -> list:
        return [{"side": util.enums.EnumSide.N}, {"side": util.enums.EnumSide.E},
                {"side": util.enums.EnumSide.S}, {"side": util.enums.EnumSide.W}]

    def get_view_bbox(self): return BBOX

    def is_solid_side(self, side) -> bool: return False

    @classmethod
    def set_block_data(cls, iteminst, block):
        if hasattr(iteminst, "inventory"):
            block.inventory = iteminst.inventory.copy()

    def on_request_item_for_block(self, itemstack):
        if G.window.keys[pyglet.window.key.LCTRL] and G.player.gamemode == 1 and G.window.mouse_pressing[
                pyglet.window.mouse.MIDDLE]:
            itemstack.item.inventory = self.inventory.copy()

