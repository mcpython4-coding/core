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
import mcpython.common.entity.AbstractEntity
import mcpython.util.math
import pyglet
from mcpython import shared
from mcpython.common.container.ResourceStack import ItemStack
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class ItemEntity(mcpython.common.entity.AbstractEntity.AbstractEntity):
    """
    Class for the item entity in the world

    Highly experimental!
    """

    NAME = "minecraft:item_entity"
    SUMMON_ABLE = False

    def __init__(
        self, *args, representing_item_stack: ItemStack = None, pickup_delay=0, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.item_stack = representing_item_stack
        self.pickup_delay = pickup_delay

        # only for test reasons here
        self.test_block = shared.registry.get_by_name("minecraft:block")["minecraft:red_carpet"]()

    def draw(self):
        self.test_block.position = self.position
        shared.model_handler.draw_block(self.test_block)

    def tick(self, dt):
        super().tick(dt)

        if self.item_stack.is_empty():
            self.kill(force=True)

    def write_to_network_buffer(self, buffer: WriteBuffer):
        super().write_to_network_buffer(buffer)
        self.item_stack.write_to_network_buffer(buffer)
        buffer.write_int(self.pickup_delay)

    def read_from_network_buffer(self, buffer: ReadBuffer):
        super().read_from_network_buffer(buffer)
        if self.item_stack is None:
            self.item_stack = ItemStack()
        self.item_stack.read_from_network_buffer(buffer)
        self.pickup_delay = buffer.read_int()
