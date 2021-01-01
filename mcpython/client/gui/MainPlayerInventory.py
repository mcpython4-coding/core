"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.client.gui.Inventory
import mcpython.client.gui.Slot
import mcpython.common.container.ItemStack
import mcpython.common.container.crafting.CraftingManager
import mcpython.common.container.crafting.CraftingGridHelperInterface
import mcpython.common.item.AbstractArmorItem
import mcpython.ResourceLoader
import PIL.Image
import mcpython.util.texture
import mcpython.common.event.EventHandler


class MainPlayerInventory(mcpython.client.gui.Inventory.Inventory):
    """
    inventory class for the main part of the inventory
    """

    TEXTURE = None
    TEXTURE_SIZE = None

    @classmethod
    def update_texture(cls):
        texture = mcpython.ResourceLoader.read_image(
            "minecraft:gui/container/inventory"
        )
        size = texture.size
        texture = texture.crop((0, 0, 176 / 255 * size[0], 164 / 255 * size[1]))
        size = texture.size
        texture = texture.resize((size[0] * 2, size[1] * 2), PIL.Image.NEAREST)
        ground = PIL.Image.new("RGBA", (texture.size[0], texture.size[1] + 4))
        ground.paste(texture)
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(ground)
        cls.TEXTURE_SIZE = ground.size

    def __init__(self, hotbar):
        self.hotbar = hotbar
        super().__init__()
        inputs = [self.slots[40:42], self.slots[42:44]]
        self.recipe_interface = mcpython.common.container.crafting.CraftingGridHelperInterface.CraftingGridHelperInterface(
            inputs, self.slots[44]
        )

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/player_inventory_main.json"

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
                    mcpython.common.item.AbstractArmorItem.AbstractArmorItem,
                ):
                    points += slot.get_itemstack().item.DEFENSE_POINTS
        shared.world.get_active_player().armor_level = points

    def draw(self, hovering_slot=None):
        """
        draws the inventory
        """
        self.bg_image_size = self.TEXTURE_SIZE
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)
        for slot in (
            shared.world.get_active_player().inventory_main.slots[:36] + self.slots
        ):
            slot.draw(x, y, hovering=slot == hovering_slot)
        for slot in (
            shared.world.get_active_player().inventory_main.slots[:36] + self.slots
        ):
            slot.draw_label()

    def remove_items_from_crafting(self):
        for slot in self.slots[40:-2]:
            slot: mcpython.client.gui.Slot.Slot
            itemstack = slot.get_itemstack()
            slot.set_itemstack(
                mcpython.common.container.ItemStack.ItemStack.create_empty()
            )
            if not shared.world.get_active_player().pick_up(itemstack):
                pass  # todo: drop item as item could not be added to inventory
        self.slots[-2].get_itemstack().clean()

    def on_deactivate(self):
        self.remove_items_from_crafting()
        shared.state_handler.active_state.parts[0].activate_mouse = True

    def update_shift_container(self):
        shared.inventory_handler.shift_container.container_A = (
            self.slots[:9] + self.slots[36:41]
        )
        shared.inventory_handler.shift_container.container_B = self.slots[9:36]


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", MainPlayerInventory.update_texture
)
