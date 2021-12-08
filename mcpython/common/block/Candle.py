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
import mcpython.common.block.PossibleBlockStateBuilder
from mcpython import shared
from mcpython.common.block import AbstractBlock
from mcpython.common.block.FlowerLikeBlock import FlowerLikeBlock
from pyglet.window import key, mouse


class ICandleGroup(AbstractBlock.AbstractBlock):
    """
    Base class for the candle block system
    """

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

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

    async def on_player_interaction(
        self,
        player,
        button: int,
        modifiers: int,
        hit_position: tuple,
        itemstack,
    ):
        if itemstack.get_item_name() != self.NAME:
            return False
        if self.count == 4:
            return False
        if button != mouse.RIGHT:
            return False
        if modifiers & key.MOD_SHIFT:
            return False

        # Don't add candles when the player is in gamemode 1
        if player.gamemode == 3:
            return False

        self.count += 1
        self.face_info.update(True)

        if player.gamemode != 1:
            itemstack.add_amount(-1)

        return True


class ICandleCake(FlowerLikeBlock):
    SUPPORT_BLOCK_TAG = None

    IS_SOLID = False
    DEFAULT_FACE_SOLID = 0

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_bool("lit")
        .build()
    )

    def __init__(self):
        super().__init__()
        self.lit = True

    def get_model_state(self):
        return {"lit": str(self.lit).lower()}

    def set_model_state(self, state: dict):
        if "lit" in state:
            self.lit = state["lit"] == "true"

    async def on_player_interaction(
        self,
        player,
        button: int,
        modifiers: int,
        hit_position: tuple,
        itemstack,
    ):
        if button != mouse.RIGHT:
            return False
        if modifiers & key.MOD_SHIFT:
            return False
        if player.gamemode == 3:
            return False

        if player.gamemode == 1:
            self.consum_bite()
            return True

        elif player.hunger < 20 and player.gamemode == 0:
            player.hunger = min(player.hunger + 4)
            self.consum_bite()
            return

    def consume_bite(self):
        # todo: consume bite on target
        shared.world.get_dimension_by_name(self.dimension).add_block(
            self.position, "minecraft:cake"
        )  # .consume_bite()
