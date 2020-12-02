"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.client.gui.Inventory
import mcpython.client.gui.Slot
import mcpython.client.gui.ItemStack
import mcpython.client.gui.crafting.CraftingManager
import mcpython.client.gui.crafting.CraftingGridHelperInterface
import mcpython.common.item.ItemArmor


class MainPlayerInventory(mcpython.client.gui.Inventory.Inventory):
    """
    inventory class for the main part of the inventory
    """

    def __init__(self, hotbar):
        self.hotbar = hotbar
        super().__init__()
        inputs = [self.slots[40:42], self.slots[42:44]]
        self.recipeinterface = mcpython.client.gui.crafting.CraftingGridHelperInterface.CraftingGridHelperInterface(
            inputs, self.slots[44]
        )

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/playerinventorymain.json"

    def create_slots(self) -> list:
        # 9x hotbar, 27x main, 4x armor, 5x crafting, 1x offhand
        return (
            [self.hotbar.slots[i].copy() for i in range(9)]
            + [mcpython.client.gui.Slot.Slot() for _ in range(27)]
            + [
                mcpython.client.gui.Slot.Slot(
                    allow_player_add_to_free_place=False, on_update=self.armor_update
                )
                for _ in range(4)
            ]
            + [
                mcpython.client.gui.Slot.Slot(allow_player_add_to_free_place=False)
                for _ in range(5)
            ]
            + [mcpython.client.gui.Slot.Slot()]
        )

    def armor_update(self, player=None):
        # todo: add toughness
        # todo: move to player
        points = 0
        for slot in self.slots[35:40]:
            if slot.get_itemstack().item:
                if issubclass(
                    type(slot.get_itemstack().item),
                    mcpython.common.item.ItemArmor.ItemArmor,
                ):
                    points += slot.get_itemstack().item.DEFENSE_POINTS
        G.world.get_active_player().armor_level = points

    def remove_items_from_crafting(self):
        for slot in self.slots[40:-2]:
            slot: mcpython.client.gui.Slot.Slot
            itemstack = slot.get_itemstack()
            slot.set_itemstack(mcpython.client.gui.ItemStack.ItemStack.get_empty())
            if not G.world.get_active_player().pick_up(itemstack):
                pass  # todo: drop item as item could not be added to inventory
        self.slots[-2].get_itemstack().clean()

    def on_deactivate(self):
        self.remove_items_from_crafting()
        G.statehandler.active_state.parts[0].activate_mouse = True

    def update_shift_container(self):
        G.inventoryhandler.shift_container.container_A = (
            self.slots[:9] + self.slots[36:41]
        )
        G.inventoryhandler.shift_container.container_B = self.slots[9:36]
