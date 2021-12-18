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
from mcpython import shared
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
from mcpython.util.enums import EnumSide


class FallingBlockEntity(mcpython.common.entity.AbstractEntity.AbstractEntity):
    """
    Class for the falling block entity

    todo: can we replicate some original block behaviour, like inventories, interaction, ...?
        -> Capability mirror?
    """

    NAME = "minecraft:falling_block"

    def __init__(self, *args, representing_block=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.block = representing_block  # todo: store in nbt
        self.nbt_data["motion"] = (0, -0.4, 0)

    def draw(self):
        if self.block is not None and shared.IS_CLIENT:
            self.block.position = self.position
            shared.model_handler.draw_block(self.block)  # todo: use batch

    async def tick(self, dt):
        await super().tick(dt)

        if self.block is None:
            await self.kill()
            return

        x, y, z = mcpython.util.math.normalize(self.position)
        block = self.chunk.get_block((x, y - 1, z))

        if (self.position[1] - y <= 0.1) and not (block is None or type(block) == str):
            if not block.is_face_solid(EnumSide.UP.bitflag):
                self.dimension.spawn_itemstack_in_world(
                    self.block.NAME, self.position, pickup_delay=0
                )
            else:
                await self.chunk.add_block((x, y, z), self.block)
                await self.kill()

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        await super().write_to_network_buffer(buffer)

        if self.block is not None:
            buffer.write_bool(True)
            buffer.write_string(self.block.NAME)
            await self.block.write_to_network_buffer(buffer)
        else:
            buffer.write_bool(False)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        await super().read_from_network_buffer(buffer)

        has_block = buffer.read_bool()
        if has_block:
            self.block = shared.registry.get_by_name("minecraft:block")[
                buffer.read_string()
            ]()
            await self.block.read_from_network_buffer(buffer)
