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
import asyncio

import mcpython.client.gui.ContainerRenderer
import mcpython.client.gui.Slot
import mcpython.common.container.crafting.CraftingGridHelperInterface
import mcpython.common.container.crafting.CraftingManager
import mcpython.common.container.ResourceStack
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader
import mcpython.util.texture
import PIL.Image
import pyglet
from mcpython import shared


class InventoryChest(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    Inventory class for chest
    Defines the default chest layout
    """

    TEXTURE = None
    TEXTURE_SIZE = None

    @classmethod
    def update_texture(cls):
        texture = mcpython.engine.ResourceLoader.read_image(
            "minecraft:gui/container/shulker_box"
        )
        size = texture.size
        texture = texture.crop((0, 0, 176 / 255 * size[0], 166 / 255 * size[1]))
        size = texture.size
        texture = texture.resize((size[0] * 2, size[1] * 2), PIL.Image.NEAREST)
        cls.TEXTURE = mcpython.util.texture.to_pyglet_image(texture)
        cls.TEXTURE_SIZE = texture.size

    @staticmethod
    def get_config_file() -> str or None:
        return "assets/config/inventory/block_inventory_chest.json"

    def __init__(self, block=None):
        super().__init__()
        self.block = None
        if self.custom_name is None and block is not None:
            self.custom_name = block.DEFAULT_DISPLAY_NAME

    async def on_activate(self):
        await super().on_activate()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "user:keyboard:press", self.on_key_press
        )

        if self.block is not None:
            if self.custom_name is None:
                self.custom_name = self.block.DEFAULT_DISPLAY_NAME

            self.block.face_info.custom_renderer.play_open_animation(self.block)

    async def on_deactivate(self):
        await super().on_deactivate()
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.unsubscribe(
            "user:keyboard:press", self.on_key_press
        )

        if self.block is not None:
            self.block.face_info.custom_renderer.play_close_animation(self.block)

    # todo: move to container
    async def create_slot_renderers(self) -> list:
        # 3 rows of 9 slots of storage
        return [mcpython.client.gui.Slot.Slot() for _ in range(9 * 3)]

    def draw(self, hovering_slot=None):
        self.bg_image_size = self.TEXTURE_SIZE
        x, y = self.get_position()
        self.TEXTURE.blit(x, y)

        super().draw(hovering_slot)

    def get_interaction_slots(self):
        return shared.world.get_active_player().inventory_main.slots[:36] + self.slots

    async def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.E:
            await shared.inventory_handler.hide(self)

    def update_shift_container(self):
        shared.inventory_handler.shift_container_handler.container_A = (
            shared.world.get_active_player().inventory_main.slots[:36]
        )
        shared.inventory_handler.shift_container_handler.container_B = self.slots


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "data:reload:work", InventoryChest.update_texture
)
