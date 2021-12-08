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
from mcpython.client.gui.InventoryFurnace import InventoryFurnace
from mcpython.common.block.IHorizontalOrientableBlock import IHorizontalOrientableBlock
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython.util.enums import EnumSide
from pyglet.window import key, mouse


class Furnace(IHorizontalOrientableBlock):
    """
    Class for the furnace block
    """

    # the list of recipe groups to use for this furnace
    FURNACE_RECIPES = ["minecraft:smelting"]

    NAME: str = "minecraft:furnace"

    DEBUG_WORLD_BLOCK_STATES = (
        mcpython.common.block.PossibleBlockStateBuilder.PossibleBlockStateBuilder()
        .add_comby_bool("active")
        .add_comby_side_horizontal("facing")
        .build()
    )

    HARDNESS = BLAST_RESISTANCE = 3.5
    ASSIGNED_TOOLS = {mcpython.util.enums.ToolType.PICKAXE}

    def __init__(self):
        """
        Creates a furnace block
        """
        super().__init__()
        self.active = False

        self.inventory = InventoryFurnace(self, self.FURNACE_RECIPES)

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)
        self.inventory.write_to_network_buffer(buffer)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)
        self.inventory.read_from_network_buffer(buffer)

    def get_model_state(self) -> dict:
        return {"facing": self.face.normal_name, "lit": str(self.active).lower()}

    def set_model_state(self, state: dict):
        super().set_model_state(state)
        if "lit" in state:
            self.active = state["lit"] == "true"

    async def on_player_interaction(
        self, player, button, modifiers, exact_hit, itemstack
    ) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            if shared.IS_CLIENT:
                await shared.inventory_handler.show(self.inventory)

            return True

        else:
            return False

    def get_inventories(self):
        return [self.inventory]

    def get_provided_slot_lists(self, side):
        if side == EnumSide.TOP:
            return [self.inventory.slots[36]], []
        elif side == EnumSide.DOWN:
            return [], [self.inventory.slots[38]]
        else:
            return [self.inventory.slots[37]], []

    async def on_block_remove(self, reason):
        # todo: add special flag for not dropping
        if shared.world.gamerule_handler.table["doTileDrops"].status.status:
            dimension = shared.world.get_dimension_by_name(self.dimension)

            for slot in self.inventory.slots:
                if slot.get_itemstack().is_empty():
                    continue

                dimension.spawn_itemstack_in_world(
                    slot.get_itemstack().copy(), self.position, pickup_delay=4
                )
                slot.get_itemstack().clean()

        if shared.IS_CLIENT:
            await shared.inventory_handler.hide(self.inventory)
            del self.inventory


class BlastFurnace(Furnace):
    NAME: str = "minecraft:blast_furnace"

    FURNACE_RECIPES = ["minecraft:blasting"]


class Smoker(Furnace):
    NAME: str = "minecraft:smoker"

    FURNACE_RECIPES = ["minecraft:smoking"]
