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

import mcpython.common.config
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer
import mcpython.engine.network.NetworkManager


class Client2ServerHandshake(AbstractPackage):
    """
    Package to be send from the client to the server on connection
    """
    CAN_GET_ANSWER = True

    def __init__(self):
        super().__init__()
        self.game_version = mcpython.common.config.VERSION_ID
        self.player_name = ""

    def setup(self, player_name: str):
        self.player_name = player_name
        return self

    def read_from_buffer(self, buffer: ReadBuffer):
        self.game_version = buffer.read_int()
        self.player_name = buffer.read_string()

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_int(self.game_version).write_string(self.player_name)

    def handle_inner(self):
        logger.println(f"client named {self.player_name} (game version: {self.game_version}) is connecting to this server")

        # todo: some better lookup
        if self.game_version != mcpython.common.config.VERSION_ID:
            logger.println("denied connection due to incompatible versions")
            self.answer(Server2ClientHandshake().setup_deny(f"Incompatible game version: {self.game_version}; expected: {mcpython.common.config.VERSION_ID}"))
            return


class Server2ClientHandshake(AbstractPackage):
    """
    The package send from the server back to the client
    Contains some meta information
    """

    def __init__(self):
        super().__init__()
        self.accept_connection = True
        self.deny_reason = ""

        self.mod_list: typing.List[typing.Tuple[str, str]] = []

    def setup_deny(self, reason: str):
        self.accept_connection = False
        self.deny_reason = reason
        return self

    def read_from_buffer(self, buffer: ReadBuffer):
        self.accept_connection = buffer.read_bool()

        if not self.accept_connection:
            self.deny_reason = buffer.read_string()
            return

        self.mod_list = buffer.read_list(
            lambda: (buffer.read_string(), buffer.read_string())
        )

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_bool(self.accept_connection)

        if not self.accept_connection:
            buffer.write_string(self.deny_reason)
            return

        buffer.write_list(
            self.mod_list, lambda e: buffer.write_string(e[0]).write_string(e[1])
        )

    def handle_inner(self):
        if not self.accept_connection:
            logger.println(
                f"[SERVER-MSG][ERROR] connection stopped; reason: {self.deny_reason}"
            )


shared.NETWORK_MANAGER.register_package_type(Client2ServerHandshake)
shared.NETWORK_MANAGER.register_package_type(Server2ClientHandshake)
