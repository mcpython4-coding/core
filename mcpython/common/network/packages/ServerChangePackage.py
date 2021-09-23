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
from mcpython.common.network.connection import connectClient2Server
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class ServerChangePackage(AbstractPackage):
    """
    Package server -> client sending a request to change the server
    """
    PACKAGE_NAME = "minecraft:server_change"

    def __init__(self):
        super().__init__()
        self.new_server_ip = "localhost"
        self.new_server_port = 8088

    def set_new_address(self, ip: str, port: int):
        self.new_server_ip = ip
        self.new_server_port = port
        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.new_server_ip)
        buffer.write_int(self.new_server_port)

    def read_from_buffer(self, buffer: ReadBuffer):
        self.new_server_ip = buffer.read_string()
        self.new_server_port = buffer.read_int()

    def handle_inner(self):
        logger.println("[NETWORK][INFO] Preparing for server change, please stand by for new connection...")
        shared.tick_handler.schedule_once(self.reconnect)
        shared.NETWORK_MANAGER.disconnect()

    def reconnect(self):
        pair = self.new_server_ip, self.new_server_port
        if not connectClient2Server(pair[0], int(pair[1])):
            logger.println("[NETWORK][FATAL] server change FAILED. See above for reason")
            shared.state_handler.change_state("minecraft:start_menu")
            return

        logger.println("[NETWORK][INFO] Server connection established")

        from mcpython.common.network.packages.HandShakePackage import (
            Client2ServerHandshake,
        )

        shared.NETWORK_MANAGER.send_package(
            Client2ServerHandshake().setup("test:player")
        )

        shared.state_handler.change_state("minecraft:server_connecting")

