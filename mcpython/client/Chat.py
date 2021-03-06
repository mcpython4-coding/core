"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import html
import time

import clipboard
import pyglet
from pyglet.window import key

from mcpython import shared, logger
import mcpython.server.command.CommandHandler
import mcpython.common.event.EventBus
import mcpython.common.event.EventHandler
import mcpython.client.gui.ContainerRenderer
import mcpython.util.opengl
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class ChatInventory(mcpython.client.gui.ContainerRenderer.ContainerRenderer):
    """
    main class for chat
    """

    def __init__(self):
        """
        creates an new Chat-instance
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
        updates the text displayed by the chat
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

    def on_activate(self):
        """
        called by the system on activation of the inventory
        """
        shared.chat.text = ""
        shared.chat.active_index = 0
        shared.chat.has_entered_t = False
        self.eventbus.activate()

    def on_deactivate(self):
        """
        called by the system on deactivation of the inventory
        """
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
    main class for chat
    """

    def __init__(self):
        """
        creates an new chat
        """
        self.text: str = ""
        self.history: list = []
        self.history_index = -1
        self.active_index = -1
        self.CANCEL_INPUT = False
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "hotkey:clear_chat", self.clear
        )

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

    def on_key_press(self, symbol: int, modifiers: int):
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
            self.CANCEL_INPUT = False
            shared.event_handler.call("chat:text_enter", self.text)
            logger.println(
                "[CHAT][INFO] entered text: '{}'".format(self.text), console=False
            )
            if self.CANCEL_INPUT:
                self.history.insert(0, self.text)
                self.close()
                return
            if self.text.startswith("/"):
                # execute command
                shared.command_parser.parse(self.text)
            else:
                self.print_ln(self.text)
            self.history.insert(0, self.text)
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
        shared.inventory_handler.hide(shared.world.get_active_player().inventory_chat)
        self.active_index = 0

    def clear(self):
        """
        will clear the chat
        """
        self.history.clear()


shared.chat = Chat()
