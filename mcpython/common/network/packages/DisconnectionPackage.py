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
import mcpython.common.event.TickHandler
from mcpython import shared
from mcpython.engine import logger
from mcpython.engine.network.AbstractPackage import AbstractPackage
from mcpython.engine.network.util import ReadBuffer, WriteBuffer


class DisconnectionInitPackage(AbstractPackage):
    CAN_GET_ANSWER = True
    PACKAGE_TYPE_ID = 3
    PACKAGE_NAME = "minecraft:disconnection_init"

    def __init__(self):
        super().__init__()
        self.reason = ""

    def set_reason(self, reason: str):
        self.reason = reason
        return self

    async def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.reason)

    async def read_from_buffer(self, buffer: ReadBuffer):
        self.reason = buffer.read_string()

    async def handle_inner(self):
        await self.answer(DisconnectionConfirmPackage())

        mcpython.common.event.TickHandler.handler.bind(self.disconnect, 5)

        if shared.IS_CLIENT:
            logger.println(
                "[NETWORK][INFO] got disconnection package from server, disconnecting..."
            )
            logger.println(self.reason)

    def disconnect(self):
        shared.NETWORK_MANAGER.disconnect(self.sender_id)


class DisconnectionConfirmPackage(AbstractPackage):
    PACKAGE_TYPE_ID = 4
    PACKAGE_NAME = "minecraft:disconnection_confirm"

    async def handle_inner(self):
        shared.NETWORK_MANAGER.disconnect(self.target_id)

        if shared.IS_CLIENT:
            await shared.world.cleanup()
            shared.state_handler.change_state("minecraft:start_menu")
