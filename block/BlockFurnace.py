import globals as G
import block.Block
from pyglet.window import key, mouse
import gui.InventoryFurnace


@G.registry
class BlockFurnace(block.Block.Block):
    @staticmethod
    def get_name(): return "minecraft:furnace"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.facing = "north"
        self.active = False
        self.inventory = gui.InventoryFurnace.InventoryFurnace(self)

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

    def on_player_interact(self, itemstack, button, modifiers, exact_hit) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            G.inventoryhandler.show(self.inventory)
            return True
        else:
            return False

    def get_inventories(self): return [self.inventory]

    def get_provided_slots(self, side): return self.inventory.slots

    def on_remove(self):
        for slot in self.inventory.slots:
            G.player.add_to_free_place(slot.itemstack.copy())
            slot.itemstack.clean()
        G.inventoryhandler.hide(self.inventory)
        del self.inventory

