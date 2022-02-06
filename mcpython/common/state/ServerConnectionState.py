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
from pyglet.window import key

from .AbstractState import AbstractState
from .ConfigBackgroundPart import ConfigBackground
from .ui.UIPartLabel import UIPartLabel
from mcpython.engine import logger
from mcpython import shared
from mcpython.engine.network.packages.DisconnectionPackage import DisconnectionInitPackage


class ConnectingToServerState(AbstractState):
    NAME = "minecraft:server_connecting"

    def __init__(self):
        self.config_background = None
        self.connecting_label = None

        super().__init__()

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    def create_state_parts(self) -> list:
        self.config_background = ConfigBackground()
        self.connecting_label = UIPartLabel(
            "Connecting to server...",
            (0, 0),
            anchor_lable="MM",
            anchor_window="MM",
            text_size=20,
            color=(255, 255, 255, 255),
        )

        return [self.config_background, self.connecting_label]

    async def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            await shared.world.cleanup()
            await shared.NETWORK_MANAGER.send_package(DisconnectionInitPackage().set_reason("User interrupted"))
            await shared.NETWORK_MANAGER.fetch_as_client()
            await shared.NETWORK_MANAGER.disconnect()

            logger.println("interrupted server connection by user")

            await shared.state_handler.change_state("minecraft:start_menu")


connecting2server = ConnectingToServerState()
