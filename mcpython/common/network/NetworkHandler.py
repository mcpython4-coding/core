"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.network.NetworkChannel
import mcpython.common.network.packages.AbstractPackage
import mcpython.common.network.NetworkConnector
from mcpython import shared


class NetworkHandler:
    def __init__(self, side: mcpython.common.network.NetworkConnector.SideType):
        self.side = side

    def register_channel(self, channel: mcpython.common.network.NetworkChannel.Channel):
        pass

    def send_package(
        self, package: mcpython.common.network.packages.AbstractPackage.AbstractPackage
    ):
        pass

    def fetch_packages(self):
        pass


if shared.IS_CLIENT:
    shared.CLIENT_NETWORK_HANDLER = NetworkHandler(
        mcpython.common.network.NetworkConnector.SideType.CLIENT
    )

shared.SERVER_NETWORK_HANDLER = NetworkHandler(
    mcpython.common.network.NetworkConnector.SideType.SERVER
)
