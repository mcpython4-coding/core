"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.client.gui.InventoryChest
import pyglet
import mcpython.common.event.EventHandler
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
    def create_slots(self) -> list:
        slots = super().create_slots()
        for slot in slots:
            slot.disallowed_item_tags = ["#minecraft:shulkerbox_like_items"]
        return slots
