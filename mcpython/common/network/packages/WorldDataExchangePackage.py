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
import itertools
import time
import traceback
import typing

from mcpython import shared
from mcpython.common.world.NetworkSyncedImplementation import NetworkSyncedDimension
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer

from .DisconnectionPackage import DisconnectionInitPackage
from .PlayerInfoPackages import PlayerInfoPackage


class DataRequestPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:world_data_request"

    def __init__(self):
        super().__init__()
        self.request_world_info_state = False
        self.request_player_info_state = False

        self.requested_dimensions = []
        self.requested_chunks = []

    def request_world_info(self):
        self.request_world_info_state = True
        return self

    def request_dimension_info(self, name: str):
        self.requested_dimensions.append(name)
        return self

    def request_chunk(self, dimension: str, cx: int, cz: int):
        # traceback.print_stack()
        self.requested_chunks.append((dimension, cx, cz))
        return self

    def request_player_info(self):
        self.request_player_info_state = True
        return self

    async def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_bool(self.request_world_info_state)
        buffer.write_bool(self.request_player_info_state)
        await buffer.write_list(self.requested_dimensions, buffer.write_string)
        await buffer.write_list(
            self.requested_chunks,
            lambda e: buffer.write_string(e[0]).write_int(e[1]).write_int(e[1]),
        )

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.request_world_info_state = buffer.read_bool()
        self.request_player_info_state = buffer.read_bool()
        self.requested_dimensions = [e async for e in buffer.read_list(buffer.read_string)]
        self.requested_chunks = [e async for e in buffer.read_list(
            lambda: (buffer.read_string(), buffer.read_int(), buffer.read_int())
        )]

    async def handle_inner(self):
        if self.request_world_info_state:
            await self.answer(WorldInfoPackage().setup())

        if self.request_player_info_state:
            await self.answer(PlayerInfoPackage().setup())

        for dimension in self.requested_dimensions:
            await self.answer(DimensionInfoPackage().setup(dimension))

        for dim, cx, cz in self.requested_chunks:
            logger.println(f"collecting chunk information for chunk @{cx}:{cz}@{dim}")
            await self.answer(ChunkDataPackage().setup(dim, (cx, cz)))


class WorldInfoPackage(AbstractPackage):
    """
    Package server -> client for sending requested data back to client.

    Mostly only for sync stuff, but dimensions should be created when needed
    """

    PACKAGE_NAME = "minecraft:world_info"

    def __init__(self):
        super().__init__()
        self.dimensions = []
        self.spawn_point = 0, 0

    def setup(self):
        self.spawn_point = shared.world.spawn_point

        for dim_id, dim in shared.world.dimensions.items():
            self.dimensions.append(
                (dim.get_name(), dim_id, dim.get_world_height_range())
            )

        return self

    async def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_int(self.spawn_point[0]).write_int(self.spawn_point[1])

        await buffer.write_list(
            self.dimensions,
            lambda e: buffer.write_string(e[0])
            .write_int(e[1])
            .write_int(e[2][0])
            .write_int(e[2][1]),
        )

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.spawn_point = buffer.read_int(), buffer.read_int()

        self.dimensions = [e async for e in buffer.read_list(
            lambda: (
                buffer.read_string(),
                buffer.read_int(),
                (buffer.read_int(), buffer.read_int()),
            )
        )]

    async def handle_inner(self):
        shared.world.spawn_point = self.spawn_point

        for name, dim_id, height_range in self.dimensions:
            logger.println(f"[NETWORK][WORLD] got dimension info of dimension '{name}'")

            dim = shared.world.get_dimension_by_name(name)

            if not isinstance(dim, NetworkSyncedDimension):
                logger.println(
                    "[NETWORK][WORLD] exchanging for a network sync-ed one..."
                )

                for chunk in dim.chunk_iterator():
                    chunk.hide()

                new_dim = shared.world.dimensions[
                    dim.get_dimension_id()
                ] = NetworkSyncedDimension(
                    shared.world,
                    dim.get_dimension_id(),
                    dim.get_name(),
                    dim.world_generation_config,
                )
                new_dim.world_generation_config_objects = (
                    dim.world_generation_config_objects
                )

                for entity in dim.entity_iterator():
                    entity.dimension = new_dim

            if dim.get_dimension_id() != dim_id:
                await self.answer(
                    DisconnectionInitPackage().set_reason("world dim id miss-match")
                )

            if dim.get_world_height_range() != height_range:
                await self.answer(
                    DisconnectionInitPackage().set_reason("world height miss-match")
                )


class DimensionInfoPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:dimension_info"

    def __init__(self):
        super().__init__()

    def setup(self, dimension: str):
        return self


class ChunkDataPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:chunk_data"

    def __init__(self):
        super().__init__()
        self.dimension = "overworld"
        self.position = 0, 0
        self.force = False

        self.blocks = []

    def setup(self, dim: str, position: typing.Tuple[int, int], force=False):
        self.dimension = dim
        self.position = position
        self.force = force

        chunk = shared.world.get_dimension_by_name(dim).get_chunk(position)

        dx, dz = chunk.position[0] * 16, chunk.position[1] * 16

        for x, y, z in itertools.product(range(16), range(256), range(16)):
            x += dx
            z += dz

            b = chunk.get_block((x, y, z), none_if_str=True)
            self.blocks.append(b)

        return self

    async def write_to_buffer(self, buffer: WriteBuffer):
        start = time.time()
        logger.println(
            f"preparing chunk data for chunk @{self.position[0]}:{self.position[1]}@{self.dimension} for networking"
        )
        chunk = shared.world.get_dimension_by_name(self.dimension).get_chunk(
            self.position
        )

        buffer.write_string(self.dimension)
        buffer.write_int(self.position[0]).write_int(self.position[1])
        buffer.write_bool(self.force)

        for b in self.blocks:
            if b is None:
                buffer.write_bool_group([False, False])
            else:
                buffer.write_bool_group([True, chunk.exposed(b.position)])
                buffer.write_string(b.NAME)
                await b.write_to_network_buffer(buffer)

        logger.println(f"-> chunk data ready (took {time.time() - start}s)")

    async def read_from_buffer(self, buffer: ReadBuffer):
        start = time.time()
        logger.println(
            f"preparing chunk data for chunk @{self.position[0]}:{self.position[1]}@{self.dimension} to world"
        )

        self.dimension = buffer.read_string()
        self.position = buffer.read_int(), buffer.read_int()
        self.force = buffer.read_bool()

        for _ in range(16 * 256 * 16):
            is_block, visible = buffer.read_bool_group(2)

            if not is_block:
                self.blocks.append(None)
            else:
                name = buffer.read_string()
                instance = shared.registry.get_by_name("minecraft:block").get(name)()
                await instance.read_from_network_buffer(buffer)
                self.blocks.append((instance, visible))

        logger.println(f"-> chunk data ready (took {time.time() - start}s)")

    async def handle_inner(self):
        start = time.time()
        logger.println(
            f"adding chunk data for chunk @{self.position[0]}:{self.position[1]}@{self.dimension} to world"
        )
        chunk = shared.world.get_dimension_by_name(self.dimension).get_chunk(
            self.position
        )

        if chunk.loaded and not self.force:
            logger.println("-> skipping as chunk exists in game")
            return

        dx, dz = self.position

        i = 0
        for x, y, z in itertools.product(
            range(dx * 16, dx * 16 + 16), range(256), range(dz * 16, dz * 16 + 16)
        ):
            block = self.blocks[i]

            if block is not None:
                await chunk.add_block(
                    (x, y, z),
                    block[0],
                    immediate=False,
                    block_update=False,
                    network_sync=False,
                )

            i += 1

        chunk.update_all_rendering()

        logger.println(f"-> chunk data fully added (took {time.time()-start}s)")
        chunk.loaded = True


class ChunkBlockChangePackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:chunk_block_update"

    def __init__(self):
        super().__init__()
        self.dimension = None
        self.data = []

    def set_dimension(self, dimension: str):
        self.dimension = dimension
        return self

    def change_position(
        self, position: typing.Tuple[int, int, int], block, update_only=False
    ):
        """
        Updates the block data at a given position
        :param position: the position
        :param block: the block instance
        :param update_only: if to only update the block, not add a new one
        """
        self.data.append((position, block, update_only))
        return self

    async def write_to_network_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.dimension)

        async def write(e):
            position, block, update_only = e
            buffer.write_long(position[0])
            buffer.write_long(position[1])
            buffer.write_long(position[2])

            if block is None:
                buffer.write_bool_group([False, False])
            else:
                buffer.write_bool_group([True, update_only])
                buffer.write_string(block.NAME)
                await block.write_to_network_buffer(buffer)

        await buffer.write_list(self.data, write)

    async def read_from_network_buffer(self, buffer: ReadBuffer):
        self.dimension = buffer.read_string()

        dimension = shared.world.get_dimension_by_name(self.dimension)

        async def read():
            position = tuple((buffer.read_long() for _ in range(3)))

            is_block, update_only = buffer.read_bool_group(2)

            if not is_block:
                self.data.append((position, None, update_only))
            else:
                name = buffer.read_string()

                if update_only:
                    b = dimension.get_block(position, none_if_str=True)

                    if b is None:
                        logger.println(
                            f"[WARM] got block internal update for block {position} in {self.dimension}, but no block is there!"
                        )
                        return

                    await b.read_from_network_buffer(buffer)

                else:
                    instance = shared.registry.get_by_name("minecraft:block").get(
                        name
                    )()
                    await instance.read_from_network_buffer(buffer)
                    self.data.append((position, instance, update_only))

        self.data = [e async for e in buffer.read_list(read)]

    async def handle_inner(self):
        dimension = shared.world.get_dimension_by_name(self.dimension)

        for position, block, update_only in self.data:
            await dimension.add_block(
                position, block, network_sync=False, block_update=False
            )
