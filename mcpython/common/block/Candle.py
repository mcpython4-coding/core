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
from pyglet.window import mouse

from mcpython.common.block import AbstractBlock
from mcpython.common.block.FlowerLikeBlock import FlowerLikeBlock
import mcpython.common.block.PossibleBlockStateBuilder


class ICandleGroup(FlowerLikeBlock):
    """
    Base class for the candle block system
    """

    # We do ignore the block type underneath, it should be only full
    SUPPORT_BLOCK_TAG = None

    IS_SOLID = False
    DEFAULT_FACE_SOLID = AbstractBlock.AbstractBlock.UNSOLID_FACE_SOLID

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby("candles", "1", "2", "3", "4")
        .add_comby_bool("lit")
        .build()
    )

    def __init__(self):
        super().__init__()
        self.count = 1
        self.lit = True

    def get_model_state(self):
        return {"candles": str(self.count), "lit": str(self.lit).lower()}

    def set_model_state(self, state: dict):
        if "candles" in state:
            self.count = int(state["candles"])

        if "lit" in state:
            self.lit = state["lit"] == "true"

    def on_player_interaction(
        self,
        player,
        button: int,
        modifiers: int,
        hit_position: tuple,
        itemstack,
    ):
        if itemstack.get_item_name() != self.NAME: return False
        if self.count == 4: return False
        if button != mouse.RIGHT: return False

        # Don't add candles when the player is in gamemode 1
        if player.gamemode == 3: return False

        self.count += 1
        self.face_info.update(True)

        if player.gamemode != 1:
            itemstack.add_amount(-1)

        return True

