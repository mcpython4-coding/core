"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.common.block.IHorizontalOrientableBlock
from pyglet.window import key, mouse
import mcpython.client.gui.InventoryFurnace
from mcpython.util.enums import EnumSide


class BlockFurnace(
    mcpython.common.block.IHorizontalOrientableBlock.IHorizontalOrientableBlock
):
    """
    class for the furnace block
    """

    FURNACE_RECIPES: list = [
        "minecraft:smelting"
    ]  # the list of recipe groups to use for this furnace

    NAME: str = "minecraft:furnace"

    def __init__(self, *args, **kwargs):
        """
        creates an furnace block in the world
        """
        super().__init__(*args, **kwargs)
        self.active = False
        self.inventory = mcpython.client.gui.InventoryFurnace.InventoryFurnace(
            self, self.FURNACE_RECIPES
        )

    def get_model_state(self) -> dict:
        return {"facing": self.face.normal_name, "lit": str(self.active).lower()}

    def set_model_state(self, state: dict):
        super().set_model_state(state)
        if "lit" in state:
            self.active = state["lit"] == "true"

    DEBUG_WORLD_BLOCK_STATES = [
        {
            mcpython.common.block.IHorizontalOrientableBlock.IHorizontalOrientableBlock.MODEL_FACE_NAME: face.name,
            "active": "false",
        }
        for face in mcpython.util.enums.EnumSide.iterate()[2:]
    ] + [
        {
            mcpython.common.block.IHorizontalOrientableBlock.IHorizontalOrientableBlock.MODEL_FACE_NAME: face.name,
            "active": "true",
        }
        for face in mcpython.util.enums.EnumSide.iterate()[2:]
    ]

    def on_player_interaction(self, player, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventory_handler.show(self.inventory)
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

    def on_block_remove(self, reason):
        if not G.world.gamerulehandler.table["doTileDrops"].status.status:
            return
        for slot in self.inventory.slots:
            G.world.get_active_player().pick_up(slot.itemstack.copy())
            slot.itemstack.clean()
        G.inventory_handler.hide(self.inventory)
        del self.inventory


class BlastFurnace(BlockFurnace):
    NAME: str = "minecraft:blast_furnace"

    FURNACE_RECIPES: list = ["minecraft:blasting"]


class Smoker(BlockFurnace):
    NAME: str = "minecraft:smoker"

    FURNACE_RECIPES: list = ["minecraft:smoking"]


@G.mod_loader("minecraft", "stage:block:load")
def load():
    G.registry.register(BlockFurnace)
    G.registry.register(BlastFurnace)
    G.registry.register(Smoker)
