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
from mcpython.util.math import vector_distance, vector_negate, vector_offset


class ItemEntity(mcpython.common.entity.AbstractEntity.AbstractEntity):
    """
    Class for the item entity in the world

    Experimental!

    todo: add real item rendering
    todo: check during attraction for collisions with blocks
    """

    NAME = "minecraft:item_entity"
    SUMMON_ABLE = False

    # todo: make this decidable by the item
    ATTRACTION_DISTANCE = 8
    PICKUP_DISTANCE = 1
    ATTRACTION_SPEED = 1

    def __init__(
        self, *args, representing_item_stack: ItemStack = None, pickup_delay=0, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.item_stack = representing_item_stack
        self.pickup_delay = pickup_delay

        # only for test reasons here
        self.test_block = shared.registry.get_by_name("minecraft:block")[
            "minecraft:oak_fence" if self.item_stack.is_empty() or not self.item_stack.item.HAS_BLOCK else self.item_stack.get_item_name()
        ]()

    def draw(self):
        self.test_block.position = self.position
        shared.model_handler.draw_block_scaled(self.test_block, .2)

    def tick(self, dt):
        super().tick(dt)

        if self.pickup_delay > 0:
            self.pickup_delay -= dt

            self.pickup_delay = max(self.pickup_delay, 0)

        if self.item_stack.is_empty():
            self.kill(force=True)

        for player in self.dimension.get_world().player_iterator():
            if player.dimension == self.dimension:
                p = player.position
                p = p[0], p[1] - 1, p[2]

                d = vector_distance(self.position, p)

                # Attract the item to the player
                if d <= self.ATTRACTION_DISTANCE:
                    v = vector_offset(p, self.position)

                    v = tuple(e / self.ATTRACTION_SPEED * dt for e in v)

                    self.position = vector_offset(self.position, vector_negate(v))

                if d <= self.PICKUP_DISTANCE and self.pickup_delay == 0:
                    player.pick_up_item(self.item_stack)
                    self.kill()

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
