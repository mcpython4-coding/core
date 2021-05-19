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

import mcpython.common.network.Backend
import mcpython.common.network.package.AbstractPackage
from mcpython import shared


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
            typing.Type[
                mcpython.common.network.package.AbstractPackage.AbstractPackage
            ],
        ] = {}
        self.custom_package_handlers: typing.Dict[
            int, typing.List[typing.Callable]
        ] = {}
        self.general_package_handlers: typing.Dict[
            int, typing.List[typing.Callable]
        ] = {}

        self.next_package_type_id = 0
        self.next_package_id = 0

        self.client_id = -1

        # Filled during handshake
        self.valid_package_ids = set()

    def send_package(
        self,
        package: mcpython.common.network.package.AbstractPackage.AbstractPackage,
        destination: int = 0,
    ):
        assert (
            package.PACKAGE_TYPE_ID != -1
        ), "package must be registered for sending it"

        encoded_head = (
            package.PACKAGE_TYPE_ID << 2 + 2
            if package.CAN_GET_ANSWER
            else 0 + 1
            if package.previous_packages
            else 0
        ).to_bytes(3, "big", signed=False)

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
            if package.previous_packages
            else package.previous_packages[-1].to_bytes(4, "big", signed=False)
        )

        package_data = package.encode()

        package_size_data = len(package_data).to_bytes(3, "big", signed=False)

        data = (
            encoded_head
            + package_id_data
            + previous_package_id_data
            + package_size_data
            + package_data
        )

    def register_package_handler(
        self,
        package_type: typing.Type[
            mcpython.common.network.package.AbstractPackage.AbstractPackage
        ],
        handler: typing.Callable[
            [mcpython.common.network.package.AbstractPackage.AbstractPackage], None
        ],
    ):
        self.general_package_handlers.setdefault(
            package_type.PACKAGE_TYPE_ID, []
        ).append(handler)
        return self

    def register_answer_handler(
        self,
        previous_package: mcpython.common.network.package.AbstractPackage.AbstractPackage,
        handler: typing.Callable[
            [mcpython.common.network.package.AbstractPackage.AbstractPackage], None
        ],
    ):
        self.custom_package_handlers.setdefault(previous_package.package_id, []).append(
            handler
        )
        return self

    def register_package_type(
        self,
        t: typing.Type[mcpython.common.network.package.AbstractPackage.AbstractPackage],
    ):
        if t.PACKAGE_TYPE_ID == -1:
            t.DYNAMIC_PACKAGE_ID = True
            while self.next_package_type_id in self.package_types:
                self.next_package_type_id += 1
            t.PACKAGE_TYPE_ID = self.next_package_type_id
        elif t.PACKAGE_TYPE_ID in self.package_types:
            other = self.package_types[t.PACKAGE_TYPE_ID]
            assert (
                other.DYNAMIC_PACKAGE_ID
            ), f"package id conflict between {t} and {other}, both forcing {t.PACKAGE_TYPE_ID}"

            # We need for the other a new package id
            while self.next_package_type_id in self.package_types:
                self.next_package_type_id += 1
            self.package_types[self.next_package_type_id] = other

        self.package_types[t.PACKAGE_TYPE_ID] = t
        return self

    def clean_network_graph(self):
        self.valid_package_ids.clear()
        self.custom_package_handlers.clear()


shared.NETWORK_MANAGER = NetworkManager()
