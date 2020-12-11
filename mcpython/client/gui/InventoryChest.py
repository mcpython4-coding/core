"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
import mcpython.client.gui.Inventory
import mcpython.client.gui.Slot
import mcpython.common.container.ItemStack
import mcpython.client.gui.crafting.CraftingManager
import mcpython.client.gui.crafting.CraftingGridHelperInterface
import mcpython.common.container.ItemStack
import pyglet
import mcpython.common.event.EventHandler
import mcpython.ResourceLoader
import PIL.Image
import mcpython.util.texture


class InventoryChest(mcpython.client.gui.Inventory.Inventory):
    """
    inventory class for chest
    """

    TEXTURE = None
    TEXTURE_SIZE = None

    @classmethod
    def update_texture(cls):
        texture = mcpython.ResourceLoader.read_image("minecraft:gui/container/shulker_box")
        size = texture.size
        texture = texture.crop((0, 0, 176/255*size[0], 166/255*size[1]))
        size = texture.size
        texture = texture.resize((size[0]*2, size[1]*2), PIL.Image.NEAREST)
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(texture)
        cls.TEXTURE_SIZE = texture.size

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/block_inventory_chest.json"

    def on_activate(self):
        super().on_activate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )

    def on_deactivate(self):
        super().on_deactivate()
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )

    def create_slots(self) -> list:
        # 3 rows of 9 slots of storage
        return [mcpython.client.gui.Slot.Slot() for _ in range(9 * 3)]

    def draw(self, hoveringslot=None):
        self.bg_image_size = self.TEXTURE_SIZE
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)
        for slot in (
            shared.world.get_active_player().inventories["main"].slots[:36] + self.slots
        ):
            slot.draw(x, y, hovering=slot == hoveringslot)
        for slot in (
            shared.world.get_active_player().inventories["main"].slots[:36] + self.slots
        ):
            slot.draw_label()

    def get_interaction_slots(self):
        return shared.world.get_active_player().inventories["main"].slots[:36] + self.slots

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            shared.inventoryhandler.hide(self)

    def update_shift_container(self):
        shared.inventoryhandler.shift_container.container_A = (
            shared.world.get_active_player().inventories["main"].slots[:36]
        )
        shared.inventoryhandler.shift_container.container_B = self.slots


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("data:reload:work", InventoryChest.update_texture)
