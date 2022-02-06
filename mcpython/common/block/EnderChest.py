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
import mcpython.client.rendering.blocks.ChestRenderer
import mcpython.common.block.PossibleBlockStateBuilder
import mcpython.util.enums
from mcpython import shared
from mcpython.common.block.Chest import BBOX
from pyglet.window import key, mouse

from . import IHorizontalOrientableBlock


class EnderChest(IHorizontalOrientableBlock.IHorizontalOrientableBlock):
    """
    class for the ender chest
    todo: check if it can be opened like in chests
    todo: fix renderer
    """

    NAME = "minecraft:enderchest"
    DEFAULT_DISPLAY_NAME = "Ender Chest"
    MODEL_FACE_NAME = "side"

    DEFAULT_FACE_SOLID = 0
    HARDNESS = 22.5
    BLAST_RESISTANCE = 600
    MINIMUM_TOOL_LEVEL = 1
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.PICKAXE}

    if shared.IS_CLIENT:
        CHEST_BLOCK_RENDERER = None

        @classmethod
        async def reload(cls):
            cls.CHEST_BLOCK_RENDERER = (
                mcpython.client.rendering.blocks.ChestRenderer.ChestRenderer(
                    "minecraft:entity/chest/ender"
                )
            )

        async def on_block_added(self):
            self.face_info.custom_renderer = self.CHEST_BLOCK_RENDERER

    async def on_player_interaction(
        self,
        player,
        button: int,
        modifiers: int,
        hit_position: tuple,
        itemstack,
    ):
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            player.inventory_enderchest.block = self
            if shared.IS_CLIENT:
                await shared.inventory_handler.show(player.inventory_enderchest)
            return True
        else:
            return False

    async def set_model_state(self, state: dict):
        if "side" in state:
            face = state["side"]

            if type(face) == str:
                self.face = mcpython.util.enums.EnumSide[state["side"].upper()]
            else:
                self.face = face

    def get_model_state(self) -> dict:
        return {"side": self.face.normal_name}

    def get_view_bbox(self):
        return BBOX

    async def on_block_remove(self, reason):
        if shared.IS_CLIENT:
            await shared.inventory_handler.hide(
                shared.world.get_active_player().inventory_enderchest
            )


if shared.IS_CLIENT:
    shared.tick_handler.schedule_once(EnderChest.reload())
