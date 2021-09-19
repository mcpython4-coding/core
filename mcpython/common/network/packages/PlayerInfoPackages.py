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
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


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
