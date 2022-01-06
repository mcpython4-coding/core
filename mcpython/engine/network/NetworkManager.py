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
import asyncio
import gzip
import io
import struct
import typing

import mcpython.engine.network.AbstractPackage
import mcpython.engine.network.Backend
from mcpython import shared
from mcpython.engine.world.AbstractInterface import IChunk
from . import AbstractPackage

from .. import logger
from .util import ReadBuffer, WriteBuffer


class NetworkManager:
    """
    THE network manager
    Abstracts packages away from the end user
    Destinations are no longer "addresses", they are ID's, where 0 is the server and players start at 1

    Data to transmit is now hold in "Packages", encoded in the following way:
        [3B-2Bi package type id][1Bi has id, 1Bi has answer id]
        [4B package id, if answering or answer is expected]
        [4B previous package id, if answer]
        [1B package compression enable]
        [3B package size]
        [package data, encoded by the package]
    """

    def __init__(self):
        self.package_types: typing.Dict[
            int,
            typing.Type[mcpython.engine.network.AbstractPackage.AbstractPackage],
        ] = {}
        self.name2package_type = {}

        self.custom_package_handlers: typing.Dict[
            int, typing.List[typing.Callable]
        ] = {}
        self.general_package_handlers: typing.Dict[
            int, typing.List[typing.Callable]
        ] = {}

        self.next_package_type_id = 1
        self.next_package_id = 0

        self.client_id = -1
        self.valid_client_ids = set()

        # Filled during handshake
        self.valid_package_ids = set()

        self.client_profiles = {}

        self.playername2connectionID = {}

    async def request_chunk(self, chunk: IChunk):
        """
        Creates a chunk request package to be sent to the server

        :param chunk: the chunk to get data for
        """

        if not shared.IS_CLIENT or not shared.IS_NETWORKING:
            raise RuntimeError

        from mcpython.common.network.packages.WorldDataExchangePackage import (
            DataRequestPackage,
        )

        await self.send_package(
            DataRequestPackage().request_chunk(
                chunk.get_dimension().get_name(), *chunk.get_position()
            )
        )

    async def send_to_player_chat(self, player: typing.Union[str, int], msg: str):
        """
        Helper function for displaying a message in a player chat

        :param player: the player name or the client id
        :param msg: the message itself
        :raises AssertionError: if the message is not a string
        """
        assert isinstance(msg, str), "message must be string"

        from mcpython.common.network.packages.PlayerChatPackage import (
            PlayerMessageShowPackage,
        )

        if isinstance(player, str):
            if player not in self.playername2connectionID:
                return

            player = self.playername2connectionID[player]

        await self.send_package(PlayerMessageShowPackage().setup(msg), player)

    def reset_package_registry(self):
        """
        Resets the internal package registry system to being empty
        Used only in unit tests to make sure that we are in a known state
        """
        self.next_package_type_id = 1
        self.package_types.clear()
        self.name2package_type.clear()

    def get_dynamic_id_info(self) -> typing.Iterator[typing.Tuple[str, int]]:
        """
        Creates the dynamic id info data, storing the package ids set by the NetworkManager at runtime,
        so multiple sources are safe to register packages, without conflicts
        """
        for package_id, package_type in self.package_types.items():
            if package_type.DYNAMIC_PACKAGE_ID:
                yield package_type.PACKAGE_NAME, package_id

    async def set_dynamic_id_info(self, data: typing.List[typing.Tuple[str, int]]):
        """
        Helper function for writing the dynamic id info data created by get_dynamic_id_info()
        Will set the package ids as needed

        :param data: the data
        """

        logger.println("[NETWORK][SYNC] starting package ID sync...")

        reassign = set()
        assigned = set()

        for name, package_id in data:
            if name not in self.name2package_type:
                logger.println(f"[NETWORK][SYNC][WARN] server knows about package '{name}' with id {package_id}, but we don't, this can cause issues!")
                continue

            package_type: typing.Type[
                mcpython.engine.network.AbstractPackage.AbstractPackage
            ] = self.name2package_type[name]
            package_id_here = package_type.PACKAGE_TYPE_ID

            if package_type in reassign:
                reassign.remove(package_type)
            assigned.add(package_type)

            logger.println(f"[NETWORK][SYNC] considering package '{name}' (client id {package_id_here}, expected from server: {package_id})")

            if package_id_here == package_id:
                continue

            logger.println(
                f"[NETWORK][SYNC] transforming {package_id_here} -> {package_id}"
            )

            self.package_types[package_id] = package_type

            if package_id_here in self.package_types:
                if self.package_types[package_id_here] not in assigned:
                    reassign.add(self.package_types[package_id_here])

                del self.package_types[package_id_here]

            if package_id_here in self.general_package_handlers:
                self.general_package_handlers[
                    package_id
                ] = self.general_package_handlers[package_id_here]
                del self.general_package_handlers[package_id_here]

        for package_class in reassign:
            previous = package_class.PACKAGE_TYPE_ID
            while self.next_package_type_id in self.package_types:
                self.next_package_type_id += 1

            package_class.PACKAGE_TYPE_ID = self.next_package_type_id
            self.package_types[package_class.PACKAGE_TYPE_ID] = package_class
            logger.println(f"[NETWORK][SYNC][WARN] client knows about package '{package_class.PACKAGE_NAME}', "
                           f"but the server wants another package at it's id, so we need to reassign it's id to "
                           f"{package_class.PACKAGE_TYPE_ID} (previous: {previous})")

        await shared.event_handler.call_async("minecraft:package_rearrangement")

        logger.println("[NETWORK][SYNC] package ID sync was successful!")

    async def disconnect(self, target=-1):
        """
        Disconnection helper, does send the disconnection package

        :param target: which one to disconnect, -1 to all directly connected (server: all, client: server)
        """
        logger.println(
            f"disconnecting connection to {target if target != -1 else ('all' if not shared.IS_CLIENT else 'server')}"
        )

        if shared.IS_CLIENT:
            shared.CLIENT_NETWORK_HANDLER.disconnect()
            await shared.state_handler.change_state("minecraft:start_menu")
        else:
            if target == -1:
                shared.SERVER_NETWORK_HANDLER.disconnect_all()
            else:
                shared.SERVER_NETWORK_HANDLER.disconnect_client(target)

    async def send_package_to_all(self, package: AbstractPackage.AbstractPackage, not_including=-1):
        """
        Sends a package to all clients in the network, excluding the given client id

        :param package: the package to send
        :param not_including: which client id to not include, or -1 if no one should be skipped
        :raises RuntimeError: if the package has no package ID, so no static id nor registered to a NetworkManager
            instance
        """
        if package.PACKAGE_TYPE_ID == -1:
            raise RuntimeError(
                f"{package}: Package type must be registered for sending it"
            )

        await asyncio.gather(
            *(
                self.send_package(package, client_id)
                for client_id in self.valid_client_ids
                if client_id != not_including
            )
        )

    async def send_package(
        self,
        package: mcpython.engine.network.AbstractPackage.AbstractPackage,
        destination: int = 0,
    ):
        """
        Sends the given package over the network to the target PC

        :param package: the package to send
        :param destination: the destination to send to, 0 is server, and clients are starting at 1
        :raises RuntimeError: if the package has no package ID, so no static id nor registered to a NetworkManager
            instance
        :raises ValueError: if the destination is 0, and we are on the server
        """
        data = await self.encode_package(destination, package)

        if shared.IS_CLIENT:
            if destination == 0:
                await shared.CLIENT_NETWORK_HANDLER.send_package(data)
            else:
                from mcpython.common.network.packages.PackageReroutingPackage import (
                    PackageReroute,
                )

                # todo: do not encode package above there!
                await self.send_package(
                    PackageReroute().set_package(destination, package), 0
                )

        else:
            if destination == 0:
                raise ValueError("destination must be non-zero on server")

            await shared.SERVER_NETWORK_HANDLER.send_package(data, destination)

    def register_package_handler(
        self,
        package_type: typing.Type[
            mcpython.engine.network.AbstractPackage.AbstractPackage
        ],
        handler: typing.Callable[
            [mcpython.engine.network.AbstractPackage.AbstractPackage], None
        ],
    ):
        """
        Registers a handler to be invoked when a certain package is received

        :param package_type: the package type to look for
        :param handler: the handler
        """
        self.general_package_handlers.setdefault(
            package_type.PACKAGE_TYPE_ID, []
        ).append(handler)
        return self

    def register_answer_handler(
        self,
        previous_package: mcpython.engine.network.AbstractPackage.AbstractPackage,
        handler: typing.Callable[
            [mcpython.engine.network.AbstractPackage.AbstractPackage, int], None
        ],
    ):
        """
        Registers a handler for when an answer is received for a given package

        :param previous_package: the package to wait for
        :param handler: the handler method
        """
        self.custom_package_handlers.setdefault(previous_package.package_id, []).append(
            handler
        )
        return self

    def register_package_type(
        self,
        package_class: typing.Type[mcpython.engine.network.AbstractPackage.AbstractPackage],
    ):
        """
        Registers a certain package class to this network manager

        :param package_class: the class to register
        """
        if package_class.PACKAGE_NAME is None:
            raise ValueError(package_class)

        if package_class.PACKAGE_TYPE_ID == -1:
            package_class.DYNAMIC_PACKAGE_ID = True
            while self.next_package_type_id in self.package_types:
                self.next_package_type_id += 1
            package_class.PACKAGE_TYPE_ID = self.next_package_type_id

        if package_class.PACKAGE_TYPE_ID in self.package_types:
            other = self.package_types[package_class.PACKAGE_TYPE_ID]

            if not other.DYNAMIC_PACKAGE_ID:
                raise RuntimeError(
                    f"package id conflict between {package_class} and {other}, both forcing {package_class.PACKAGE_TYPE_ID}"
                )

            # We need for the other a new package id
            while self.next_package_type_id in self.package_types:
                self.next_package_type_id += 1

            self.package_types[self.next_package_type_id] = other

        self.package_types[package_class.PACKAGE_TYPE_ID] = package_class

        self.name2package_type[package_class.PACKAGE_NAME] = package_class

        return self

    async def fetch_as_client(self):
        """
        Util method invoked on the client to fetch data from the socket and handle it
        """

        if not shared.CLIENT_NETWORK_HANDLER.connected:
            return

        shared.CLIENT_NETWORK_HANDLER.work()
        buffer = ReadBuffer(shared.CLIENT_NETWORK_HANDLER.data_stream)
        shared.CLIENT_NETWORK_HANDLER.data_stream.clear()

        while buffer:
            try:
                package = await self.fetch_package_from_buffer(buffer)
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                logger.print_exception("during fetching package data @client")
                await self.disconnect()
                return

            if package is None:
                break

            package.sender_id = 0

            try:
                await package.handle_inner()
            except (SystemExit, KeyboardInterrupt):
                raise
            except:
                logger.print_exception(f"during handling package {package} @client")
                continue

            if package.PACKAGE_TYPE_ID in self.general_package_handlers:
                for func in self.general_package_handlers[package.PACKAGE_TYPE_ID]:
                    result = func(package, self.client_id)
                    if isinstance(result, typing.Awaitable):
                        await result

            if package.package_id in self.custom_package_handlers:
                for func in self.custom_package_handlers[package.package_id]:
                    result = func(package, self.client_id)
                    if isinstance(result, typing.Awaitable):
                        await result

                self.custom_package_handlers[package.package_id].clear()

    async def fetch_as_server(self):
        """
        Util method invoked on the server to fetch data from the socket and handle it
        """

        for client_id, buffer in shared.SERVER_NETWORK_HANDLER.get_package_streams():
            buffer = ReadBuffer(buffer)

            while buffer:
                try:
                    package = await self.fetch_package_from_buffer(buffer)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except:
                    logger.print_exception(
                        f"during fetching data @server from @{client_id}"
                    )
                    await self.disconnect(client_id)
                    break

                if package is None:
                    return

                package.sender_id = client_id

                try:
                    await package.handle_inner()
                except (SystemExit, KeyboardInterrupt):
                    raise
                except:
                    logger.print_exception(
                        f"during handling package {package} @server from @{client_id}"
                    )
                    continue

                if package.PACKAGE_TYPE_ID in self.general_package_handlers:
                    for func in self.general_package_handlers[package.PACKAGE_TYPE_ID]:
                        result = func(package, 0)
                        if isinstance(result, typing.Awaitable):
                            await result

                if package.package_id in self.custom_package_handlers:
                    for func in self.custom_package_handlers[package.package_id]:
                        result = func(package, 0)
                        if isinstance(result, typing.Awaitable):
                            await result

                    self.custom_package_handlers[package.package_id].clear()

    def clean_network_graph(self):
        """
        Cleans some internal stuff
        """
        self.valid_package_ids.clear()
        self.custom_package_handlers.clear()
        self.next_package_type_id = 1

    async def encode_package(self, destination: int, package: AbstractPackage.AbstractPackage) -> bytes:
        """
        Encodes the given package to bytes

        :param destination: where to send to
        :param package: the package to encode
        :return: the bytes representing the package
        :raises RuntimeError: if the package has no package ID, so no static id nor registered to a NetworkManager
            instance
        """
        if package.PACKAGE_TYPE_ID == -1:
            raise RuntimeError(
                f"{package}: Package type must be registered for sending it"
            )

        buffer = WriteBuffer()

        package.target_id = destination

        buffer.write_uint(package.PACKAGE_TYPE_ID)
        buffer.write_bool_group((package.CAN_GET_ANSWER, bool(package.previous_packages)))

        if package.CAN_GET_ANSWER and package.package_id == -1:
            package.package_id = self.next_package_id
            self.next_package_id += 1

        if package.CAN_GET_ANSWER:
            buffer.write_uint(package.package_id)

        if package.previous_packages:
            await buffer.write_list(package.previous_packages, lambda e: buffer.write_uint(e))

        pbuf = WriteBuffer()
        await package.write_to_buffer(pbuf)
        package_data = pbuf.get_data()

        compress_data = len(package_data) > 200 and package.ALLOW_PACKAGE_COMPRESSION

        if compress_data:
            package_data = gzip.compress(package_data)

        buffer.write_bool(compress_data)

        buffer.write_bytes(package_data, size_size=3)

        return buffer.get_data()

    async def fetch_package_from_buffer(self, buffer: ReadBuffer, log_package_error=True) -> AbstractPackage.AbstractPackage | None:
        """
        Reads a package from the network buffer instance

        :param buffer: the buffer to read from
        :param log_package_error: if to log errors with the package, or to silently ignore them
        :return: the package instance, or None if an error occurred
        """

        assert isinstance(buffer, ReadBuffer), f"buffer must be a network buffer, not {type(buffer)} ({repr(buffer)[:100]})"

        try:
            try:
                package_type = buffer.read_uint()
            except struct.error:
                return

            if not self.package_types:
                await load_packages()

            if package_type not in self.package_types:
                if log_package_error:
                    logger.println(
                        f"[NETWORK][ERROR] received unknown package type of ID {package_type}"
                    )
                    logger.println(list(self.package_types.keys()))
                return

            has_package_id, has_previous_package_id = buffer.read_bool_group(2)

            if has_package_id:
                package_id = buffer.read_uint()
            else:
                package_id = -1

            if has_previous_package_id:
                previous_ids = await buffer.collect_list(lambda: buffer.read_uint())
            else:
                previous_ids = []

            package_compressed = buffer.read_bool()

            package_data = buffer.read_bytes(size_size=3)

            if package_compressed:
                package_data = gzip.decompress(package_data)

        except IndexError:
            return

        buffer = ReadBuffer(io.BytesIO(package_data))

        package = self.package_types[package_type]()
        await package.read_from_buffer(buffer)

        package.package_id = package_id
        package.previous_packages = previous_ids

        return package


shared.NETWORK_MANAGER = NetworkManager()


async def load_packages():
    from mcpython.common.network.packages import (
        ClientStateChangePackage,
        DisconnectionPackage,
        HandShakePackage,
        PackageIDSync,
        PackageReroutingPackage,
        PlayerChatPackage,
        PlayerInfoPackages,
        RegistrySyncPackage,
        ServerChangePackage,
        WorldDataExchangePackage,
    )

    shared.NETWORK_MANAGER.register_package_type(
        HandShakePackage.Client2ServerHandshake
    )
    shared.NETWORK_MANAGER.register_package_type(
        HandShakePackage.Server2ClientHandshake
    )
    shared.NETWORK_MANAGER.register_package_type(
        DisconnectionPackage.DisconnectionInitPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        DisconnectionPackage.DisconnectionConfirmPackage
    )
    shared.NETWORK_MANAGER.register_package_type(PackageReroutingPackage.PackageReroute)
    shared.NETWORK_MANAGER.register_package_type(PackageIDSync.PackageIDSync)
    shared.NETWORK_MANAGER.register_package_type(
        RegistrySyncPackage.RegistrySyncInitPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        RegistrySyncPackage.RegistrySyncPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        RegistrySyncPackage.RegistrySyncResultPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        WorldDataExchangePackage.DataRequestPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        mcpython.common.network.packages.PlayerInfoPackages.PlayerInfoPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        mcpython.common.network.packages.PlayerInfoPackages.PlayerUpdatePackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        WorldDataExchangePackage.WorldInfoPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        WorldDataExchangePackage.DimensionInfoPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        WorldDataExchangePackage.ChunkDataPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        WorldDataExchangePackage.ChunkBlockChangePackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        PlayerChatPackage.PlayerChatInputPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        PlayerChatPackage.PlayerMessageShowPackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        PlayerChatPackage.PlayerClientCommandExecution
    )
    shared.NETWORK_MANAGER.register_package_type(
        ClientStateChangePackage.ClientStateChangePackage
    )
    shared.NETWORK_MANAGER.register_package_type(
        ServerChangePackage.ServerChangePackage
    )


if not shared.IS_TEST_ENV:
    shared.mod_loader("minecraft", "stage:network:package_register")(load_packages)
