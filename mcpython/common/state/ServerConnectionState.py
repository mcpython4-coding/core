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
from mcpython.util.annotation import onlyInClient

from .AbstractState import AbstractState
from .ConfigBackgroundPart import ConfigBackground
from .ui.UIPartLabel import UIPartLabel


class ConnectingToServerState(AbstractState):
    NAME = "minecraft:server_connecting"

    def __init__(self):
        self.config_background = None
        self.connecting_label = None

        super().__init__()

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


connecting2server = ConnectingToServerState()
