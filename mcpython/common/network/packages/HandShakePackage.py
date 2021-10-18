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
import mcpython.engine.network.NetworkManager
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer

from .PackageIDSync import PackageIDSync


class Client2ServerHandshake(AbstractPackage):
    """
    Package to be send from the client to the server on connection
    """

    CAN_GET_ANSWER = True
    PACKAGE_TYPE_ID = 1
    PACKAGE_NAME = "minecraft:client2server_handshake"

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
        logger.println(
            f"client named '{self.player_name}' (game version: {self.game_version}) is connecting to this server"
        )

        # todo: some better lookup with compatible network lookup
        if self.game_version != mcpython.common.config.VERSION_ID:
            logger.println(f"[HANDSHAKE] denied connection to {self.player_name} due to incompatible versions")
            self.answer(
                Server2ClientHandshake().setup_deny(
                    f"Incompatible game version: {self.game_version}; expected: {mcpython.common.config.VERSION_ID}"
                )
            )
            return

        if self.player_name in shared.NETWORK_MANAGER.client_profiles:
            logger.println(f"[HANDSHAKE] denied connection due to duplicate player name {self.player_name}")
            self.answer(
                Server2ClientHandshake().setup_deny(
                    f"Invalid player name: Player with same name already connected to this server"
                )
            )
            return

        shared.NETWORK_MANAGER.client_profiles.setdefault(self.sender_id, {})[
            "player_name"
        ] = self.player_name
        shared.NETWORK_MANAGER.playername2connectionID[
            self.player_name
        ] = self.sender_id

        shared.world.add_player(self.player_name)

        logger.println(f"[HANDSHAKE] sending mod list to {self.player_name}")
        self.answer(Server2ClientHandshake().setup_accept())

        logger.println(f"[HANDSHAKE] syncing up package id lists to {self.player_name}")
        self.answer(PackageIDSync().setup())


class Server2ClientHandshake(AbstractPackage):
    """
    The package send from the server back to the client
    Contains some meta information
    """

    PACKAGE_TYPE_ID = 2
    PACKAGE_NAME = "minecraft:server2client_handshake"

    def __init__(self):
        super().__init__()
        self.accept_connection = True
        self.deny_reason = ""

        self.mod_list: typing.List[typing.Tuple[str, str]] = []

    def setup_deny(self, reason: str):
        self.accept_connection = False
        self.deny_reason = reason
        return self

    def setup_accept(self):
        mod_info = []
        for mod in shared.mod_loader.mods.values():

            if not mod.server_only:
                mod_info.append((mod.name, str(mod.version)))

        shared.event_handler.call("minecraft:modlist:sync:setup", self, mod_info)
        self.mod_list = mod_info
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
                f"[SERVER-MSG][ERROR] connection closed by server; reason: {self.deny_reason}"
            )
            return

        miss_matches = []

        for modname, version in self.mod_list:
            if modname not in shared.mod_loader.mods:
                miss_matches.append(f"missing mod: {modname}")

            elif str(shared.mod_loader[modname].version) != version:
                miss_matches.append(
                    f"mod {modname} version miss-match: {version} (server) != "
                    f"{shared.mod_loader[modname].version} (client)"
                )

        if miss_matches:
            logger.write_into_container(miss_matches)

            from .DisconnectionPackage import DisconnectionInitPackage

            shared.NETWORK_MANAGER.send_package(
                DisconnectionInitPackage().set_reason("mod mismatch")
            )
            return

        logger.println(
            f"[SERVER-MSG][INFO] connection successful; compared {len(self.mod_list)} "
            f"mods and they seem equal"
        )

        logger.println("[CLIENT][INFO] starting registry compare...")
        from .RegistrySyncPackage import RegistrySyncInitPackage

        self.answer(RegistrySyncInitPackage().setup())
