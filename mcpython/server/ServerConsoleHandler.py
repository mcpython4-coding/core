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
import threading

from mcpython import logger
from mcpython import shared


class ServerConsoleHandler:
    def __init__(self):
        self.thread = threading.Thread(target=self._run)
        self.running = True

    def _run(self):
        while self.running:
            command = input(">>> ")
            if command.startswith("/"):
                shared.command_parser.run(command)
            else:
                logger.println("[SERVER]", command)

    def run(self):
        self.thread.start()


handler = ServerConsoleHandler()
