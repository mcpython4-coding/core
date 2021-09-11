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
import typing

from mcpython import shared
from mcpython.common.world.NetworkSyncedImplementation import NetworkSyncedDimension
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer

from .DisconnectionPackage import DisconnectionInitPackage


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
        self.requested_chunks.append((dimension, cx, cz))
        return self

    def request_player_info(self):
        self.request_player_info_state = True
        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_bool(self.request_world_info_state)
        buffer.write_bool(self.request_player_info_state)
        buffer.write_list(self.requested_dimensions, lambda e: buffer.write_string(e))
        buffer.write_list(
            self.requested_chunks,
            lambda e: buffer.write_string(e[0]).write_int(e[1]).write_int(e[1]),
        )

    def read_from_buffer(self, buffer: ReadBuffer):
        self.request_world_info_state = buffer.read_bool()
        self.request_player_info_state = buffer.read_bool()
        self.requested_dimensions = buffer.read_list(lambda: buffer.read_string())
        self.requested_chunks = buffer.read_list(
            lambda: (buffer.read_string(), buffer.read_int(), buffer.read_int())
        )

    def handle_inner(self):
        if self.request_world_info_state:
            self.answer(WorldInfoPackage().setup())

        if self.request_player_info_state:
            self.answer(PlayerInfoPackage().setup())

        for dimension in self.requested_dimensions:
            self.answer(DimensionInfoPackage().setup(dimension))

        for dim, cx, cz in self.requested_chunks:
            logger.println(f"collecting chunk information for chunk @{cx}:{cz}@{dim}")
            self.answer(ChunkDataPackage().setup(dim, (cx, cz)))


class PlayerInfoPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:player_info"

    def __init__(self):
        super().__init__()
        self.players = []

    def setup(self):
        self.players = list(shared.world.players.values())
        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_list(
            self.players, lambda player: player.write_to_network_buffer(buffer)
        )

    def read_from_buffer(self, buffer: ReadBuffer):
        from mcpython.common.entity.PlayerEntity import PlayerEntity

        self.players = buffer.read_list(
            lambda: PlayerEntity().read_from_network_buffer(buffer)
        )

    def handle_inner(self):
        for player in self.players:
            shared.entity_manager.spawn_entity(player, player.position)
            shared.world.players[player.name] = player

            logger.println(
                f"[NETWORK] got player data for player '{player.name}'@{player.position}@{player.dimension.get_name()}"
            )


class PlayerUpdatePackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:player_info:update"

    def __init__(self):
        super().__init__()
        self.name = ""
        self.position = 0, 0, 0
        self.rotation = 0, 0, 0
        self.motion = 0, 0, 0
        self.dimension = "minecraft:overworld"
        self.selected_slot = 0
        self.gamemode = 0

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.name)
        for e in self.position + tuple(self.rotation) + self.motion:
            buffer.write_float(e)
        buffer.write_string(self.dimension)
        buffer.write_int(self.selected_slot)
        buffer.write_int(self.gamemode)

    def read_from_buffer(self, buffer: ReadBuffer):
        self.name = buffer.read_string()
        self.position = tuple(buffer.read_float() for _ in range(3))
        self.rotation = list(buffer.read_float() for _ in range(3))
        self.motion = tuple(buffer.read_float() for _ in range(3))
        self.dimension = buffer.read_string()
        self.selected_slot = buffer.read_int()
        self.gamemode = buffer.read_int()

    def handle_inner(self):
        player = shared.world.get_player_by_name(self.name)
        player.write_update_package(self)

        if not shared.IS_CLIENT:
            shared.NETWORK_MANAGER.send_package_to_all(
                self, not_including=self.sender_id
            )


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

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_int(self.spawn_point[0]).write_int(self.spawn_point[1])

        buffer.write_list(
            self.dimensions,
            lambda e: buffer.write_string(e[0])
            .write_int(e[1])
            .write_int(e[2][0])
            .write_int(e[2][1]),
        )

    def read_from_buffer(self, buffer: ReadBuffer):
        self.spawn_point = buffer.read_int(), buffer.read_int()

        self.dimensions = buffer.read_list(
            lambda: (
                buffer.read_string(),
                buffer.read_int(),
                (buffer.read_int(), buffer.read_int()),
            )
        )

    def handle_inner(self):
        shared.world.spawn_point = self.spawn_point

        for name, dim_id, height_range in self.dimensions:
            logger.println(f"[NETWORK][WORLD] got dimension info of dimension '{name}'")

            dim = shared.world.get_dimension_by_name(name)

            if not isinstance(dim, NetworkSyncedDimension):
                logger.println(
                    "[NETWORK][WORLD] exchanging for a network sync-ed one..."
                )
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
                new_dim.batches = dim.batches

            if dim.get_dimension_id() != dim_id:
                self.answer(
                    DisconnectionInitPackage().set_reason("world dim id miss-match")
                )

            if dim.get_world_height_range() != height_range:
                self.answer(
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

        self.blocks = []

    def setup(self, dim: str, position: typing.Tuple[int, int]):
        self.dimension = dim
        self.position = position

        chunk = shared.world.get_dimension_by_name(dim).get_chunk(position)

        dx, dz = chunk.position[0] * 16, chunk.position[1] * 16

        for x, y, z in itertools.product(range(16), range(256), range(16)):
            x += dx
            z += dz

            b = chunk.get_block((x, y, z), none_if_str=True)
            self.blocks.append(b)

        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        start = time.time()
        logger.println(
            f"preparing chunk data for chunk @{self.position[0]}:{self.position[1]}@{self.dimension} for networking"
        )
        chunk = shared.world.get_dimension_by_name(self.dimension).get_chunk(self.position)

        buffer.write_string(self.dimension)
        buffer.write_int(self.position[0]).write_int(self.position[1])

        for b in self.blocks:
            if b is None:
                buffer.write_string("")
            else:
                buffer.write_string(b.NAME)
                buffer.write_bool(chunk.exposed(b.position))
                b.write_to_network_buffer(buffer)

        logger.println(f"-> chunk data ready (took {time.time() - start}s)")

    def read_from_buffer(self, buffer: ReadBuffer):
        start = time.time()
        logger.println(
            f"preparing chunk data for chunk @{self.position[0]}:{self.position[1]}@{self.dimension} to world"
        )

        self.dimension = buffer.read_string()
        self.position = buffer.read_int(), buffer.read_int()

        for _ in range(16 * 256 * 16):
            name = buffer.read_string()

            if name == "":
                self.blocks.append(None)
            else:
                instance = shared.registry.get_by_name("minecraft:block").get(name)()
                visible = buffer.read_bool()
                instance.read_from_network_buffer(buffer)
                self.blocks.append((instance, visible))

        logger.println(f"-> chunk data ready (took {time.time() - start}s)")

    def handle_inner(self):
        start = time.time()
        logger.println(
            f"adding chunk data for chunk @{self.position[0]}:{self.position[1]}@{self.dimension} to world"
        )
        chunk = shared.world.get_dimension_by_name(self.dimension).get_chunk(
            self.position
        )

        if chunk.loaded:
            logger.println("-> skipping as chunk exists in game")
            return

        dx, dz = self.position

        i = 0
        for x, y, z in itertools.product(range(16), range(256), range(16)):
            x += dx
            z += dz

            block = self.blocks[i]

            if block is not None:
                chunk.add_block(
                    (x, y, z), block[0], immediate=block[1], block_update=False
                )

            i += 1

        logger.println(f"-> chunk data fully added (took {time.time()-start}s)")
        chunk.loaded = True


class ChunkUpdatePackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:chunk_update"
