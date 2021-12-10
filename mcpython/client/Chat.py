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
import asyncio
import html
import time

import clipboard
import mcpython.client.gui.ContainerRenderer
import mcpython.engine.event.EventBus
import mcpython.engine.event.EventHandler
import mcpython.server.command.CommandParser
import mcpython.util.opengl
import pyglet
from mcpython import shared
from mcpython.common.network.packages.PlayerChatPackage import PlayerChatInputPackage
from mcpython.engine import logger
from mcpython.util.annotation import onlyInClient
from pyglet.window import key


@onlyInClient()
class ChatInventory(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    Main class for chat inventory
    Every player should have one
    """

    def __init__(self):
        """
        Creates a new Chat-inventory-instance
        """
        super().__init__()
        self.label = pyglet.text.HTMLLabel("", x=15, y=15)
        self.enable_blink = True
        self.timer = time.time()
        self.eventbus = shared.event_handler.create_bus(active=False)
        self.eventbus.subscribe("user:keyboard:press", shared.chat.on_key_press)
        self.eventbus.subscribe("user:keyboard:enter", shared.chat.enter)

    def update_text(self, text: str, underline_index: int):
        """
        Updates the text displayed by the chat
        :param text: the text to use
        :param underline_index: the index where the "_" is
        """
        if len(text) < underline_index:
            self.label.text = "<font color='white'>" + text + "_</font>"
            return

        try:
            self.label.text = "<font color='white'>{}<u>{}</u>{}</font>".format(
                text[:underline_index],
                text[underline_index],
                text[1 + underline_index :],
            )

        except IndexError:
            self.label.text = (
                "<font color='white'>" + text + "<span>&#95;</span></font>"
            )

    async def on_activate(self):
        shared.chat.text = ""
        shared.chat.active_index = 0
        shared.chat.has_entered_t = False
        self.eventbus.activate()

    async def on_deactivate(self):
        self.eventbus.deactivate()

    def draw(self, hovering_slot=None):
        wx, _ = shared.window.get_size()
        mcpython.util.opengl.draw_rectangle(
            (10, 10), (wx - 20, 20), color=(0.0, 0.0, 0.0, 0.8)
        )
        text = html.escape(shared.chat.text)

        if (round(time.time() - self.timer) % 2) == 1:
            self.update_text(text, shared.chat.active_index)
        else:
            self.label.text = "<font color='white'>" + text + "</font>"

        self.label.draw()


class Chat:
    """
    Main class for chat
    """

    def __init__(self):
        self.text: str = ""  # the text currently shown
        self.history: list = []  # the previous commands
        self.history_index = -1
        self.active_index = -1
        self.CANCEL_INPUT = False
        mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:clear_chat", self.clear
        )
        self.executing_command_info = None

    def enter(self, text: str):
        """
        called when text is entered
        :param text: the text that is entered
        """
        self.text = (
            self.text[: self.active_index + 1]
            + text
            + self.text[self.active_index + 1 :]
        )
        self.active_index += len(text)

    async def on_key_press(self, symbol: int, modifiers: int):
        """
        called when an key is pressed
        :param symbol: the symbol that is pressed
        :param modifiers: the modifiers that are used
        todo: split up into parts
        """
        if symbol == 65288:  # BACK
            self.text = (
                self.text[: self.active_index - 1] + self.text[self.active_index :]
            )
            self.active_index -= 1

        elif symbol == key.DELETE and self.active_index < len(self.text):
            self.text = (
                self.text[: self.active_index] + self.text[self.active_index + 1 :]
            )

        elif symbol == 65360:  # begin key
            self.active_index = 0

        elif symbol == key.END:
            self.active_index = len(self.text)

        elif symbol == key.ENTER:  # execute command
            if shared.IS_CLIENT and shared.IS_NETWORKING:
                await shared.NETWORK_MANAGER.send_package(
                    PlayerChatInputPackage().setup(self.text)
                )

            elif self.text.startswith("/"):
                # execute command
                if self.executing_command_info is None:
                    self.executing_command_info = mcpython.server.command.CommandParser.CommandExecutionEnvironment(
                        this=shared.world.get_active_player()
                    )
                    self.executing_command_info.chat = self
                else:
                    player = shared.world.get_active_player()
                    self.executing_command_info.position = player.get_position()
                    self.executing_command_info.dimension = player.get_dimension()

                await shared.command_parser.run(self.text, self.executing_command_info)

            else:
                self.print_ln(self.text)

            self.history.insert(0, self.text)
            self.history_index = -1
            self.close()

        elif (
            symbol == key.UP and self.history_index < len(self.history) - 1
        ):  # go one item up in the history
            self.history_index += 1
            self.text = self.history[self.history_index]
            self.active_index = len(self.text)

        elif (
            symbol == key.DOWN and self.history_index >= 0
        ):  # go one item down in the history
            self.history_index -= 1
            if self.history_index != -1:
                self.text = self.history[self.history_index]
            else:
                self.text = ""
            self.active_index = len(self.text)

        elif symbol == key.LEFT:
            self.active_index -= 1
            if self.active_index < 0:
                self.active_index = len(self.text) + self.active_index + 1

        elif symbol == key.RIGHT:
            self.active_index += 1
            if self.active_index > len(self.text):
                self.active_index = 0

        elif symbol == key.V and modifiers & key.MOD_CTRL:  # insert text from clipboard
            self.enter(clipboard.paste())

    def print_ln(self, text: str):
        """
        will print an line into the chat
        :param text: the line to print
        todo: make an in-game chat an link this to there
        todo: make all commands use this as backend
        """
        logger.println("[CHAT] {}".format(text))

    def close(self):
        """
        closes the chat
        """
        shared.tick_handler.schedule_once(shared.inventory_handler.hide(shared.world.get_active_player().inventory_chat))
        self.active_index = 0

    def clear(self):
        """
        will clear the chat
        """
        self.history.clear()


shared.chat = Chat()
