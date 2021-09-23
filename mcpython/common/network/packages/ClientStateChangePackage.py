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
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class ClientStateChangePackage(AbstractPackage):
    """
    Package server -> client sending a request to change the current state
    """
    DISALLOWED_STATES = set()

    PACKAGE_NAME = "minecraft:client_state_change"

    def __init__(self):
        super().__init__()
        self.new_state = ""

    def set_state(self, new_state: str):
        self.new_state = new_state
        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.new_state)

    def read_from_buffer(self, buffer: ReadBuffer):
        self.new_state = buffer.read_string()

    def handle_inner(self):
        if self.new_state in self.DISALLOWED_STATES:
            logger.println(f"[NETWORK][FATAL] Server requested state change to state {self.new_state}, which is not allowed!")
            logger.println("[NETWORK][FATAL] this results in an unplanned disconnection...")
            shared.NETWORK_MANAGER.disconnect(self.sender_id)
        else:
            shared.state_handler.change_state(self.new_state)

