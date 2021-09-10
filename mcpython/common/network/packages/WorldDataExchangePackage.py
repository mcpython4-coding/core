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
import typing

from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


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
        for e in self.position + self.rotation + self.motion:
            buffer.write_float(e)
        buffer.write_string(self.dimension)
        buffer.write_int(self.selected_slot)
        buffer.write_int(self.gamemode)

    def read_from_buffer(self, buffer: ReadBuffer):
        self.name = buffer.read_string()
        self.position = tuple(buffer.read_float() for _ in range(3))
        self.rotation = tuple(buffer.read_float() for _ in range(3))
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
    PACKAGE_NAME = "minecraft:world_info"

    def setup(self):
        return self


class DimensionInfoPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:dimension_info"

    def setup(self, dimension):
        return self


class ChunkDataPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:chunk_data"

    def setup(self, dim, param):
        return self


class ChunkUpdatePackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:chunk_update"
