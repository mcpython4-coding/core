"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.block.Block
from pyglet.window import key, mouse
import mcpython.gui.InventoryFurnace
from mcpython.util.enums import EnumSide


@G.registry
class BlockFurnace(mcpython.block.Block.Block):
    """
    class for the furnace block
    """
    FURNACE_RECIPES: list = ["minecraft:smelting"]  # the list of recipe groups to use for this furnace

    NAME: str = "minecraft:furnace"

    def __init__(self, *args, **kwargs):
        """
        creates an furnace block in the world
        """
        super().__init__(*args, **kwargs)
        self.facing = "north"
        self.active = False
        self.inventory = mcpython.gui.InventoryFurnace.InventoryFurnace(self, self.FURNACE_RECIPES)
        if self.set_to is not None:
            dx, dy, dz = tuple([self.position[i] - self.set_to[i] for i in range(3)])
            if dx > 0:   self.facing = "south"
            elif dx < 0: self.facing = "north"
            elif dz > 0: self.facing = "west"
            elif dz < 0: self.facing = "east"

    def get_model_state(self) -> dict:
        return {"facing": self.facing, "lit": str(self.active).lower()}

    def set_model_state(self, state: dict):
        if "facing" in state: self.facing = state["facing"]
        if "lit" in state: self.active = state["lit"] == "true"

    @staticmethod
    def get_all_model_states() -> list:
        return [{"facing": "north", "lit": "false"}, {"facing": "east", "lit": "false"},
                {"facing": "south", "lit": "false"}, {"facing": "west", "lit": "false"},
                {"facing": "north", "lit": "true"}, {"facing": "east", "lit": "true"},
                {"facing": "south", "lit": "true"}, {"facing": "west", "lit": "true"}]

    def on_player_interact(self, player, itemstack, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self): return [self.inventory]

    def get_provided_slot_lists(self, side):
        if side == EnumSide.TOP:
            return [self.inventory.slots[36]], []
        elif side == EnumSide.DOWN:
            return [], [self.inventory.slots[38]]
        else:
            return [self.inventory.slots[37]], []

    def on_remove(self):
        if not G.world.gamerulehandler.table["doTileDrops"].status.status: return
        for slot in self.inventory.slots:
            G.world.get_active_player().pick_up(slot.itemstack.copy())
            slot.itemstack.clean()
        G.inventoryhandler.hide(self.inventory)
        del self.inventory


@G.registry
class BlastFurnace(BlockFurnace):
    NAME: str = "minecraft:blast_furnace"

    FURNACE_RECIPES: list = ["minecraft:blasting"]


@G.registry
class Smoker(BlockFurnace):
    NAME: str = "minecraft:smoker"

    FURNACE_RECIPES: list = ["minecraft:smoking"]
