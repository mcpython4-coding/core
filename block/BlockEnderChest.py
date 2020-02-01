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
import block.BoundingBox
from block.BlockChest import BBOX


@G.registry
class BlockChest(Block.Block):
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
        self.inventory = G.player.inventorys["enderchest"]

    @staticmethod
    def get_name() -> str:
        return "minecraft:enderchest"

    def on_player_interact(self, itemstack, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
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
        return [item.ItemTool.ToolType.PICKAXE]

    def get_provided_slots(self, side): return self.inventory.slots

    def set_model_state(self, state: dict):
        if "side" in state:
            face = state["side"]
            if type(face) == str:
                self.front_side = util.enums.EnumSide[state["side"]]
            else:
                self.front_side = face

    def get_model_state(self) -> dict:
        return {"side": self.front_side.name}

    @staticmethod
    def get_all_model_states() -> list:
        return [{"side": util.enums.EnumSide.N}, {"side": util.enums.EnumSide.E},
                {"side": util.enums.EnumSide.S}, {"side": util.enums.EnumSide.W}]

    def get_view_bbox(self): return BBOX

    def is_solid_side(self, side) -> bool: return False

