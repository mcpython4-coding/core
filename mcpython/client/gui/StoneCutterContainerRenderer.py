"""
mcpython - a minecraft clone written in python licenced under the MIT-licence
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import PIL

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.InventoryChest
import mcpython.client.gui.Slot
import mcpython.common.container.crafting.CraftingGridHelperInterface
import mcpython.common.container.crafting.CraftingManager
import mcpython.common.container.ResourceStack
import mcpython.engine.event.EventHandler
import pyglet
from mcpython import shared
import mcpython.engine.ResourceLoader


class StoneCutterContainerRenderer(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    Inventory class for the stone cutter
    May be shared across multiple stonecutters at client side
    """

    TEXTURE = None
    TEXTURE_SIZE = None

    @classmethod
    def update_texture(cls):
        import mcpython.util.texture

        texture = mcpython.engine.ResourceLoader.read_image(
            "minecraft:gui/container/stonecutter"
        )
        size = texture.size
        texture = texture.crop((0, 0, 175 / 255 * size[0], 165 / 255 * size[1]))
        size = texture.size
        texture = texture.resize((size[0] * 2, size[1] * 2), PIL.Image.NEAREST)
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(texture)
        cls.TEXTURE_SIZE = texture.size

    def __init__(self):
        super().__init__()
        if self.custom_name is None:
            self.custom_name = "Stonecutter"

        self.currently_selected = -1

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/block_inventory_stonecutter.json"

    def on_activate(self):
        super().on_activate()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )

    def on_deactivate(self):
        super().on_deactivate()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )

    # todo: move to container
    def create_slot_renderers(self) -> list:
        # 3 rows of 9 slots of storage
        return [mcpython.client.gui.Slot.Slot()] + [mcpython.client.gui.Slot.Slot(allow_player_remove=False, allow_player_insert=False, enable_hovering_background=False, allow_half_getting=False) for _ in range(3*4)] + [mcpython.client.gui.Slot.Slot()]

    def draw(self, hovering_slot=None):
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)
        self.bg_image_size = self.TEXTURE_SIZE
        super().draw(hovering_slot)

    def get_interaction_slots(self):
        return shared.world.get_active_player().inventory_main.slots[:36] + self.slots

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            shared.inventory_handler.hide(self)

    def update_shift_container(self):
        shared.inventory_handler.shift_container_handler.container_A = (
            shared.world.get_active_player().inventory_main.slots[:36]
        )
        shared.inventory_handler.shift_container_handler.container_B = (self.slots[0],) + (self.slots[-1],)


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", StoneCutterContainerRenderer.update_texture
)
