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


class AbstractPackage:
    """
    Base class for network packages
    A package may have a static or dynamic ID. Dynamic ids are given on the fly,
    static ones are checked at registration time.

    A package does not need to be arrival on both sides of a network. Each network manager holds
    a list of valid package id's, other ones will be ignored


    """

    # A unique package name, used during handshake for package type comparison
    # Can include version of the package
    PACKAGE_NAME: typing.Optional[str] = None

    # Set this to a meaningful int when needed
    PACKAGE_TYPE_ID = -1

    # DO NOT TOUCH!
    DYNAMIC_PACKAGE_ID = False

    CAN_GET_ANSWER = False

    def __init__(self):
        self.package_id = -1  # set during send process
        self.previous_packages = []  # set only during receiving or calling answer()

    def send(self, destination=0):
        shared.NETWORK_MANAGER.send_package(self, destination)

        if self.CAN_GET_ANSWER:
            shared.NETWORK_MANAGER.register_answer_handler(
                self, self.on_answer_received
            )

        return self

    def on_answer_received(self, package):
        pass

    def encode(self) -> bytes:
        raise NotImplementedError

    def answer(self, package: "AbstractPackage"):
        assert self.package_id != -1, "package ID must be set by calling send()!"

        package.previous_packages = self.previous_packages + [self.package_id]
