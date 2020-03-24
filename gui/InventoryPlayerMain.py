"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import gui.Inventory
import gui.Slot
import gui.ItemStack
import crafting.CraftingHandler
import crafting.GridRecipeInterface
import item.ItemArmor


class InventoryPlayerMain(gui.Inventory.Inventory):
    """
    inventory class for the main part of the inventory
    """

    def __init__(self, hotbar):
        self.hotbar = hotbar
        super().__init__()
        inputs = [self.slots[40:42], self.slots[42:44]]
        self.recipeinterface = crafting.GridRecipeInterface.GridRecipeInterface(inputs, self.slots[44])

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/playerinventorymain.json"

    def create_slots(self) -> list:
        # 9x hotbar, 27x main, 4x armor, 5x crafting, 1x offhand
        return [self.hotbar.slots[i].copy() for i in range(9)] + \
               [gui.Slot.Slot() for _ in range(27)] + \
               [gui.Slot.Slot(allow_player_add_to_free_place=False, on_update=self.armor_update) for _ in range(4)] + \
               [gui.Slot.Slot(allow_player_add_to_free_place=False) for _ in range(6)]

    def on_activate(self):
        pass

    def armor_update(self, player=None):
        # todo: add toughness
        # todo: move to player
        points = 0
        for slot in self.slots[35:40]:
            if slot.get_itemstack().item:
                if issubclass(type(slot.get_itemstack().item), item.ItemArmor.ItemArmor):
                    points += slot.get_itemstack().item.DEFENSE_POINTS
        G.world.get_active_player().armor_level = points

    def on_deactivate(self):
        self.slots[45].get_itemstack().clean()
        for slot in self.slots[40:-1]:
            slot: gui.Slot.Slot
            itemstack = slot.get_itemstack()
            slot.set_itemstack(gui.ItemStack.ItemStack.get_empty())
            G.world.get_active_player().pick_up(itemstack)
        G.statehandler.active_state.parts[0].activate_mouse = True

