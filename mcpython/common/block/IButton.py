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
from .IAllDirectionOrientableBlock import IAllDirectionOrientableBlock
from mcpython.util.enums import EnumSide
from mcpython import shared
from .PossibleBlockStateBuilder import PossibleBlockStateBuilder
from mcpython.common.container.ResourceStack import ItemStack


class IButton(IAllDirectionOrientableBlock):
    # todo: add a way to decide in advance if to allow setting the block

    DEBUG_WORLD_BLOCK_STATES = (
        PossibleBlockStateBuilder()
        .add_comby("face", "wall")
        .add_comby_side_horizontal("facing")
        .add_comby_bool("powered")
        .build()
    ) + (
        PossibleBlockStateBuilder()
        .add_comby("face", "floor")
        .add_comby_side_horizontal("facing")
        .add_comby_bool("powered")
        .build()
    ) + (
        PossibleBlockStateBuilder()
        .add_comby("face", "floor")
        .add_comby_side_horizontal("facing")
        .add_comby_bool("powered")
        .build()
    )

    def __init__(self):
        super().__init__()
        self.powered = False

    def on_block_added(self):
        super().on_block_added()
        self.check_block_behind()

    def check_block_behind(self):
        x, y, z = self.position
        dx, dy, dz = self.face.dx, self.face.dy, self.face.dz

        block = self.dimension.get_block((x+dx, y+dy, z+dz), none_if_str=True)

        if block is None or not block.face_solid[self.face.invert()]:
            self.dimension.remove_block(self.position, block_update_self=False)

            # todo: drop item into world
            if shared.IS_CLIENT:
                shared.world.get_active_player().pick_up_item(ItemStack(self.NAME))

    def on_block_update(self):
        self.check_block_behind()

    def get_model_state(self) -> dict:
        # todo: for floor / ceiling, use real calculations
        if self.face == EnumSide.UP:
            d = {"face": "ceiling", "facing": "north"}
        elif self.face == EnumSide.DOWN:
            d = {"face": "floor", "facing": "north"}
        else:
            d = super().get_model_state()
            d["face"] = "wall"

        d["powered"] = str(self.powered).lower()

        return d

    def set_model_state(self, state: dict):
        if state["face"] == "ceiling":
            self.face = EnumSide.UP
        elif state["face"] == "floor":
            self.face = EnumSide.DOWN
        else:
            super().set_model_state(state)
        self.powered = state["powered"] == "true"

