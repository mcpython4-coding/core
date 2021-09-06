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
import io
import typing

import mcpython.engine.network.AbstractPackage
import mcpython.engine.network.Backend
from mcpython import shared

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
        [3B package size]
        [package data, encoded by the package]
    """

    def __init__(self):
        self.package_types: typing.Dict[
            int,
            typing.Type[mcpython.engine.network.AbstractPackage.AbstractPackage],
        ] = {}
        self.custom_package_handlers: typing.Dict[
            int, typing.List[typing.Callable]
        ] = {}
        self.general_package_handlers: typing.Dict[
            int, typing.List[typing.Callable]
        ] = {}

        self.name2package_type = {}

        self.next_package_type_id = 1
        self.next_package_id = 0

        self.client_id = -1

        # Filled during handshake
        self.valid_package_ids = set()

    def get_dynamic_id_info(self) -> typing.List[typing.Tuple[str, int]]:
        d = []

        for package_id, package_type in self.package_types.items():
            if package_type.DYNAMIC_PACKAGE_ID:
                d.append((package_type.PACKAGE_NAME, package_id))

        return d

    def set_dynamic_id_info(self, data: typing.List[typing.Tuple[str, int]]):
        logger.println("[NETWORK][SYNC] starting package ID sync...")

        for name, package_id in data:
            if name not in self.name2package_type:
                continue

            package_type: typing.Type[
                mcpython.engine.network.AbstractPackage.AbstractPackage
            ] = self.name2package_type[name]
            package_id_here = package_type.PACKAGE_TYPE_ID

            logger.println(f"[NETWORK][SYNC] considering package {name}")

            if package_id_here == package_id:
                continue

            logger.println(
                f"[NETWORK][SYNC] transforming {package_id_here} -> {package_id}"
            )

            self.package_types[package_id] = package_type

            if package_id_here in self.package_types:
                del self.package_types[package_id_here]

            if package_id_here in self.general_package_handlers:
                self.general_package_handlers[
                    package_id
                ] = self.general_package_handlers[package_id_here]
                del self.general_package_handlers[package_id_here]

        shared.event_handler.call("minecraft:package_rearrangement")

        logger.println("[NETWORK][SYNC] package ID sync was successful!")

    def disconnect(self, target=-1):
        print(f"disconnecting connection to {target}")

        if shared.IS_CLIENT:
            shared.CLIENT_NETWORK_HANDLER.disconnect()
        else:
            if target == -1:
                shared.SERVER_NETWORK_HANDLER.disconnect_all()
            else:
                shared.SERVER_NETWORK_HANDLER.disconnect_client(target)

    def send_package(
        self,
        package: mcpython.engine.network.AbstractPackage.AbstractPackage,
        destination: int = 0,
    ):
        data = self.encode_package(destination, package)

        if shared.IS_CLIENT:
            if destination == 0:
                shared.CLIENT_NETWORK_HANDLER.send_package(data)
            else:
                from mcpython.common.network.packages.PackageReroutingPackage import (
                    PackageReroute,
                )

                # todo: do not encode package above there!
                self.send_package(PackageReroute().set_package(destination, package), 0)

        else:
            if destination == 0:
                raise ValueError("destination must be non-zero on server")

            shared.SERVER_NETWORK_HANDLER.send_package(data, destination)

    def encode_package(self, destination, package) -> bytes:
        if package.PACKAGE_TYPE_ID == -1:
            raise RuntimeError(
                f"{package}: Package type must be registered for sending it"
            )
        package.target_id = destination
        bit_map = (
            (package.PACKAGE_TYPE_ID << 2) + (2 if package.CAN_GET_ANSWER else 0)
        ) + (1 if package.previous_packages else 0)
        encoded_head = bit_map.to_bytes(4, "big", signed=False)
        if package.CAN_GET_ANSWER and package.package_id == -1:
            package.package_id = self.next_package_id
            self.next_package_id += 1
        package_id_data = (
            b""
            if not package.CAN_GET_ANSWER
            else package.package_id.to_bytes(4, "big", signed=False)
        )
        previous_package_id_data = (
            b""
            if not package.previous_packages
            else package.previous_packages[-1].to_bytes(4, "big", signed=False)
        )
        buffer = WriteBuffer()
        package.write_to_buffer(buffer)
        package_data = buffer.get_data()
        package_size_data = len(package_data).to_bytes(3, "big", signed=False)
        data = (
            encoded_head
            + package_id_data
            + previous_package_id_data
            + package_size_data
            + package_data
        )
        return data

    def register_package_handler(
        self,
        package_type: typing.Type[
            mcpython.engine.network.AbstractPackage.AbstractPackage
        ],
        handler: typing.Callable[
            [mcpython.engine.network.AbstractPackage.AbstractPackage], None
        ],
    ):
        self.general_package_handlers.setdefault(
            package_type.PACKAGE_TYPE_ID, []
        ).append(handler)
        return self

    def register_answer_handler(
        self,
        previous_package: mcpython.engine.network.AbstractPackage.AbstractPackage,
        handler: typing.Callable[
            [mcpython.engine.network.AbstractPackage.AbstractPackage], None
        ],
    ):
        self.custom_package_handlers.setdefault(previous_package.package_id, []).append(
            handler
        )
        return self

    def register_package_type(
        self,
        t: typing.Type[mcpython.engine.network.AbstractPackage.AbstractPackage],
    ):
        if t.PACKAGE_NAME is None:
            raise ValueError(t)

        if t.PACKAGE_TYPE_ID == -1:
            t.DYNAMIC_PACKAGE_ID = True
            while self.next_package_type_id in self.package_types:
                self.next_package_type_id += 1
            t.PACKAGE_TYPE_ID = self.next_package_type_id

        elif t.PACKAGE_TYPE_ID in self.package_types:
            other = self.package_types[t.PACKAGE_TYPE_ID]

            if not other.DYNAMIC_PACKAGE_ID:
                raise RuntimeError(
                    f"package id conflict between {t} and {other}, both forcing {t.PACKAGE_TYPE_ID}"
                )

            # We need for the other a new package id
            while self.next_package_type_id in self.package_types:
                self.next_package_type_id += 1

            self.package_types[self.next_package_type_id] = other

        self.package_types[t.PACKAGE_TYPE_ID] = t

        self.name2package_type[t.PACKAGE_NAME] = t
        return self

    def clean_network_graph(self):
        self.valid_package_ids.clear()
        self.custom_package_handlers.clear()

    def fetch_as_client(self):
        if not shared.CLIENT_NETWORK_HANDLER.connected:
            return

        shared.CLIENT_NETWORK_HANDLER.work()
        buffer = shared.CLIENT_NETWORK_HANDLER.data_stream

        while buffer:
            package = self.fetch_package_from_buffer(buffer)

            if package is None:
                return

            package.sender_id = 0
            package.handle_inner()

            if package.PACKAGE_TYPE_ID in self.general_package_handlers:
                for func in self.general_package_handlers[package.PACKAGE_TYPE_ID]:
                    func(package, self.client_id)

            if package.package_id in self.custom_package_handlers:
                for func in self.custom_package_handlers[package.package_id]:
                    func(package, self.client_id)

                self.custom_package_handlers[package.package_id].clear()

    def fetch_as_server(self):
        for client_id, buffer in shared.SERVER_NETWORK_HANDLER.get_package_streams():
            while buffer:
                package = self.fetch_package_from_buffer(buffer)

                if package is None:
                    return

                package.sender_id = client_id

                package.handle_inner()

                if package.PACKAGE_TYPE_ID in self.general_package_handlers:
                    for func in self.general_package_handlers[package.PACKAGE_TYPE_ID]:
                        func(package, 0)

                if package.package_id in self.custom_package_handlers:
                    for func in self.custom_package_handlers[package.package_id]:
                        func(package, 0)
                    self.custom_package_handlers[package.package_id].clear()

    def fetch_package_from_buffer(self, buffer):
        try:
            head = int.from_bytes(buffer[:4], "big", signed=False)

            package_type = head >> 2

            if not self.package_types:
                load_packages()

            if package_type not in self.package_types:
                logger.println(
                    f"[NETWORK][ERROR] received unknown package type of ID {package_type}"
                )
                print(list(self.package_types.keys()))
                print(buffer[:4])
                print(head)
                return

            has_package_id = head & 2
            has_previous_package_id = head & 1

            index = 4
            if has_package_id:
                package_id = int.from_bytes(
                    buffer[index : index + 4], "big", signed=False
                )
                index += 4
            else:
                package_id = -1

            if has_previous_package_id:
                previous_id = int.from_bytes(
                    buffer[index : index + 4], "big", signed=False
                )
                index += 4
            else:
                previous_id = None

            package_size = int.from_bytes(
                buffer[index : index + 3], "big", signed=False
            )
            index += 3

            package_data = buffer[index : index + package_size]

            del buffer[: index + package_size]

        except IndexError:
            return

        buffer = ReadBuffer(io.BytesIO(package_data))

        package = self.package_types[package_type]()
        package.read_from_buffer(buffer)

        package.package_id = package_id
        if previous_id:
            package.previous_packages.append(previous_id)

        return package


shared.NETWORK_MANAGER = NetworkManager()


def load_packages():
    from mcpython.common.network.packages import (
        DisconnectionPackage,
        HandShakePackage,
        PackageIDSync,
        PackageReroutingPackage,
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


shared.mod_loader("minecraft", "stage:network:package_register")(load_packages)
