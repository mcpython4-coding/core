"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from pyglet.window import mouse, key

import globals as G
import mcpython.util.enums
from mcpython.block.BlockChest import BBOX
from . import Block


class BlockEnderChest(Block.Block):
    """
    class for the ender chest
    """

    def __init__(self, *args, **kwargs):
        """
        creates the ender chest block
        """
        super().__init__(*args, **kwargs)
        self.front_side = mcpython.util.enums.EnumSide.N
        if self.real_hit:
            dx, dz = self.real_hit[0] - self.position[0], self.real_hit[1] - self.position[1]
            if dx > 0 and abs(dx) > abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.N
            elif dx < 0 and abs(dx) > abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.S
            elif dz > 0 and abs(dx) < abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.E
            elif dz < 0 and abs(dx) < abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.W
        self.inventory = G.world.get_active_player().inventories["enderchest"]
        self.face_solid = {face: False for face in mcpython.util.enums.EnumSide.iterate()}

    NAME = "minecraft:enderchest"

    def on_player_interaction(self, player, button: int, modifiers: int, hit_position: tuple):
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    HARDNESS = 2.5
    MINIMUM_TOOL_LEVEL = 0
    BEST_TOOLS_TO_BREAK = [mcpython.util.enums.ToolType.PICKAXE]

    def get_provided_slots(self, side):
        return self.inventory.slots

    def set_model_state(self, state: dict):
        if "side" in state:
            face = state["side"]
            if type(face) == str:
                self.front_side = mcpython.util.enums.EnumSide[state["side"]]
            else:
                self.front_side = face

    def get_model_state(self) -> dict:
        return {"side": self.front_side.name}

    @staticmethod
    def get_all_model_states() -> list:
        return [{"side": mcpython.util.enums.EnumSide.N}, {"side": mcpython.util.enums.EnumSide.E},
                {"side": mcpython.util.enums.EnumSide.S}, {"side": mcpython.util.enums.EnumSide.W}]

    def get_view_bbox(self):
        return BBOX

    def on_remove(self):
        G.inventoryhandler.hide(self.inventory)


@G.modloader("minecraft", "stage:block:load")
def load():
    G.registry.register(BlockEnderChest)

