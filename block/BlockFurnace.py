"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import block.Block
from pyglet.window import key, mouse
import gui.InventoryFurnace


@G.registry
class BlockFurnace(block.Block.Block):
    FURNACE_RECIPES = ["minecraft:smelting"]

    NAME = "minecraft:furnace"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.facing = "north"
        self.active = False
        self.inventory = gui.InventoryFurnace.InventoryFurnace(self, self.FURNACE_RECIPES)
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

    def get_provided_slots(self, side): return self.inventory.slots

    def on_remove(self):
        if not G.world.gamerulehandler.table["doTileDrops"].status.status: return
        for slot in self.inventory.slots:
            G.world.get_active_player().pick_up(slot.itemstack.copy())
            slot.itemstack.clean()
        G.inventoryhandler.hide(self.inventory)
        del self.inventory


@G.registry
class BlastFurnace(BlockFurnace):
    NAME = "minecraft:blast_furnace"

    FURNACE_RECIPES = ["minecraft:blasting"]


@G.registry
class Smoker(BlockFurnace):
    NAME = "minecraft:smoker"

    FURNACE_RECIPES = ["minecraft:smoking"]
