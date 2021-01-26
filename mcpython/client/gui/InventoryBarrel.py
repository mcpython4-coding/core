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
import mcpython.common.container.ItemStack
import pyglet
import mcpython.common.event.EventHandler
import mcpython.client.gui.InventoryChest


class InventoryBarrel(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    inventory class for chest
    """

    def __init__(self, block):
        super().__init__()
        self.block = block
        if self.custom_name is None:
            self.custom_name = "Barrel"

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/block_inventory_chest.json"

    def on_activate(self):
        super().on_activate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )
        self.block.opened = True
        if shared.IS_CLIENT:
            self.block.face_state.update(True)

    def on_deactivate(self):
        super().on_deactivate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )
        self.block.opened = False
        if shared.IS_CLIENT:
            self.block.face_state.update(True)

    # todo: move to container
    def create_slots(self) -> list:
        # 3 rows of 9 slots of storage
        return [mcpython.client.gui.Slot.Slot() for _ in range(9 * 3)]

    def draw(self, hovering_slot=None):
        x, y = self.get_position()
        mcpython.client.gui.InventoryChest.InventoryChest.TEXTURE.blit(x, y)
        self.bg_image_size = (
            mcpython.client.gui.InventoryChest.InventoryChest.TEXTURE_SIZE
        )
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
