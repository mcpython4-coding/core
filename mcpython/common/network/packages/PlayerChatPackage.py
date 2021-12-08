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
from mcpython.server.command.CommandParser import CommandExecutionEnvironment


class PlayerChatInputPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:player_chat_input"

    def __init__(self):
        super().__init__()
        self.text = ""

    def setup(self, text: str):
        self.text = text
        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.text)

    def read_from_buffer(self, buffer: ReadBuffer):
        self.text = buffer.read_string()

    async def handle_inner(self):
        if self.text.startswith("/"):
            player = shared.world.get_player_by_name(
                shared.NETWORK_MANAGER.client_profiles[self.sender_id]["player_name"]
            )
            env = CommandExecutionEnvironment(this=player)
            if not await shared.command_parser.run(self.text, env):
                self.answer(PlayerClientCommandExecution().setup(self.text))

        else:
            text = (
                f"[{shared.NETWORK_MANAGER.client_profiles[self.sender_id]['player_name']}] "
                + self.text
            )
            shared.NETWORK_MANAGER.send_package_to_all(
                PlayerMessageShowPackage().setup(text)
            )
            logger.println(text)


class PlayerMessageShowPackage(AbstractPackage):
    PACKAGE_NAME = "minecraft:player_chat_show"

    def __init__(self):
        super().__init__()
        self.text = ""

    def setup(self, text: str):
        self.text = text
        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.text)

    def read_from_buffer(self, buffer: ReadBuffer):
        self.text = buffer.read_string()

    async def handle_inner(self):
        logger.println(self.text)


class PlayerClientCommandExecution(AbstractPackage):
    PACKAGE_NAME = "minecraft:player_client_command"

    def __init__(self):
        super().__init__()
        self.text = ""

    def setup(self, text: str):
        self.text = text
        return self

    def write_to_buffer(self, buffer: WriteBuffer):
        buffer.write_string(self.text)

    def read_from_buffer(self, buffer: ReadBuffer):
        self.text = buffer.read_string()

    async def handle_inner(self):
        env = CommandExecutionEnvironment(this=shared.world.get_active_player())
        await shared.command_parser.run(self.text, env)
