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
from mcpython.util.annotation import onlyInClient

from .AbstractState import AbstractState
from .ConfigBackgroundPart import ConfigBackground
from .ui.UIPartButton import UIPartButton
from .ui.UIPartTextInput import UIPartTextInput


@onlyInClient()
class ServerSelectionState(AbstractState):
    NAME = "minecraft:server_selection"

    def __init__(self):
        self.config_background = None
        self.back_button = None
        self.join_button = None
        self.server_ip_input = None

        super().__init__()

    def get_parts(self) -> list:
        self.config_background = ConfigBackground()
        self.back_button = UIPartButton(
            (300, 20),
            "Back",
            (-180, 30),
            anchor_window="MD",
            anchor_button="MD",
            on_press=lambda *_: shared.state_handler.change_state(
                "minecraft:start_menu"
            ),
        )
        self.join_button = UIPartButton(
            (300, 20),
            "Join",
            (180, 30),
            anchor_window="MD",
            anchor_button="MD",
            on_press=self.open_server_connection,
        )

        self.server_ip_input = UIPartTextInput(
            (400, 30),
            (0, 60),
            anchor_ti="MD",
            anchor_window="MD",
            default_text="127.0.0.1:8088",
        )

        return [
            self.config_background,
            self.back_button,
            self.join_button,
            self.server_ip_input,
        ]

    def open_server_connection(self, *_):
        pair = self.server_ip_input.entered_text.split(":")
        if not connectClient2Server(pair[0], int(pair[1])):
            shared.state_handler.change_state("minecraft:start_menu")
            return

        from mcpython.common.network.packages.HandShakePackage import (
            Client2ServerHandshake,
        )

        shared.NETWORK_MANAGER.send_package(
            Client2ServerHandshake().setup("test:player")
        )

        shared.state_handler.change_state("minecraft:server_connecting")


server_selection = ServerSelectionState()
