"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

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
                shared.command_parser.parse(command)
            else:
                logger.println("[SERVER]", command)

    def run(self):
        self.thread.start()


handler = ServerConsoleHandler()

