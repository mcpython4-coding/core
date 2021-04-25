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
from pyglet.window import mouse, key

from mcpython import shared
import mcpython.util.enums
from mcpython.common.block.Chest import BBOX
from . import AbstractBlock
import mcpython.common.block.PossibleBlockStateBuilder


class EnderChest(AbstractBlock.AbstractBlock):
    """
    class for the ender chest
    todo: check if it can be opened like in chests
    todo: fix renderer
    """

    NAME = "minecraft:enderchest"
    DEFAULT_FACE_SOLID = (
        mcpython.common.block.AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID
    )
    HARDNESS = 2.5
    MINIMUM_TOOL_LEVEL = 0
    ASSIGNED_TOOLS = [mcpython.util.enums.ToolType.PICKAXE]

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_side_horizontal("side")
        .build()
    )

    def __init__(self):
        super().__init__()

        self.front_side = mcpython.util.enums.EnumSide.N
        self.inventory = shared.world.get_active_player().inventory_enderchest

    def on_block_added(self):
        if self.real_hit:
            dx, dz = (
                self.real_hit[0] - self.position[0],
                self.real_hit[1] - self.position[1],
            )
            if dx > 0 and abs(dx) > abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.N
            elif dx < 0 and abs(dx) > abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.S
            elif dz > 0 and abs(dx) < abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.E
            elif dz < 0 and abs(dx) < abs(dz):
                self.front_side = mcpython.util.enums.EnumSide.W

    def on_player_interaction(
        self, player, button: int, modifiers: int, hit_position: tuple
    ):
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            if shared.IS_CLIENT:
                shared.inventory_handler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    def get_provided_slots(self, side):
        return self.inventory.slots

    def set_model_state(self, state: dict):
        if "side" in state:
            face = state["side"]

            if type(face) == str:
                self.front_side = mcpython.util.enums.EnumSide[state["side"].upper()]
            else:
                self.front_side = face

    def get_model_state(self) -> dict:
        return {"side": self.front_side.normal_name}

    def get_view_bbox(self):
        return BBOX

    def on_block_remove(self, reason):
        if shared.IS_CLIENT:
            shared.inventory_handler.hide(self.inventory)
