"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.Slot
import mcpython.common.container.ItemStack
import mcpython.common.container.crafting.CraftingManager
import mcpython.common.container.crafting.CraftingGridHelperInterface
import pyglet
import mcpython.common.event.EventHandler
import mcpython.ResourceLoader
import PIL.Image
import mcpython.util.texture


class InventoryCraftingTable(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    inventory class for the crafting table
    """

    TEXTURE = None
    TEXTURE_SIZE = None

    @classmethod
    def update_texture(cls):
        texture = mcpython.ResourceLoader.read_image(
            "minecraft:gui/container/crafting_table"
        )
        size = texture.size
        texture = texture.crop((0, 0, 176 / 255 * size[0], 166 / 255 * size[1]))
        size = texture.size
        texture = texture.resize((size[0] * 2, size[1] * 2), PIL.Image.NEAREST)
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(texture)
        cls.TEXTURE_SIZE = texture.size

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/block_inventory_crafting_table.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inputs = [self.slots[:3], self.slots[3:6], self.slots[6:9]]
        self.recipeinterface = mcpython.common.container.crafting.CraftingGridHelperInterface.CraftingGridHelperInterface(
            inputs, self.slots[9]
        )
        if self.custom_name is None:
            self.custom_name = "Crafting Table"

    # todo: move to container
    def create_slot_renderers(self) -> list:
        # 36 slots of main, 9 crafting grid, 1 crafting output
        # base_slots = shared.world.get_active_player().inventory_main.slots[:36]
        return [mcpython.client.gui.Slot.Slot() for _ in range(10)]

    def on_activate(self):
        super().on_activate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )

    def on_deactivate(self):
        super().on_deactivate()
        for slot in self.slots[:-1]:
            shared.world.get_active_player().pick_up_item(slot.get_itemstack().copy())
            slot.get_itemstack().clean()
        self.slots[-1].itemstack.clean()
        self.slots[-1].get_itemstack().clean()
        shared.world.get_active_player().reset_moving_slot()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )

    def draw(self, hovering_slot=None):
        """
        draws the inventory
        """
        self.bg_image_size = self.TEXTURE_SIZE
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)
        super().draw(hovering_slot)

    def get_interaction_slots(self):
        return shared.world.get_active_player().inventory_main.slots[:36] + self.slots

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            shared.inventory_handler.hide(self)

    def update_shift_container(self):
        shared.inventory_handler.shift_container.container_A = (
            shared.world.get_active_player().inventory_main.slots[:36]
        )
        shared.inventory_handler.shift_container.container_B = self.slots


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", InventoryCraftingTable.update_texture
)
