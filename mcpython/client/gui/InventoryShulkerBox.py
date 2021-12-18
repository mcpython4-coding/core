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
import mcpython.client.gui.InventoryChest
import mcpython.engine.event.EventHandler
import pyglet
from mcpython import shared


class InventoryShulkerBox(mcpython.client.gui.InventoryChest.InventoryChest):
    """
    Class for the shulker box inventory
    Simply disables shulkerbox like items in the slots of the inventory
    """

    def __init__(self):
        super().__init__()
        if self.custom_name is None:
            self.custom_name = "Shulker Box"

    # todo: move to container & let it display the chest renderer
    async def create_slot_renderers(self) -> list:
        slots = await super().create_slot_renderers()
        for slot in slots:
            slot.disallowed_item_tags = ["#minecraft:shulkerbox_like_items"]
        return slots
