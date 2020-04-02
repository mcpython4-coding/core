"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import gui.Inventory
import util.opengl
import pyglet
from pyglet.window import key
import time
import chat.command.CommandHandler
import event.EventHandler
import event.EventBus
import clipboard
import traceback
import logger
import html


class ChatInventory(gui.Inventory.Inventory):
    """
    main class for chat
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lable = pyglet.text.HTMLLabel("", x=15, y=15)
        self.enable_blink = True
        self.timer = time.time()
        self.eventbus = G.eventhandler.create_bus(active=False)
        self.eventbus.subscribe("user:keyboard:press", G.chat.on_key_press)
        self.eventbus.subscribe("user:keyboard:enter", G.chat.enter)

    def update_text(self, text, underline_index):
        if len(text) < underline_index:
            self.lable.text = "<font color='white'>"+text+"_</font>"
            return
        try:
            self.lable.text = "<font color='white'>{}<u>{}</u>{}</font>".format(text[:underline_index],
                                                                                text[underline_index],
                                                                                text[1+underline_index:])
        except IndexError:
            self.lable.text = "<font color='white'>"+text+"<span>&#95;</span></font>"

    def on_activate(self):
        G.chat.text = ""
        G.chat.active_index = 0
        G.chat.has_entered_t = False
        self.eventbus.activate()

    def on_deactivate(self):
        self.eventbus.deactivate()

    def on_draw_background(self):
        wx, _ = G.window.get_size()
        util.opengl.draw_rectangle((10, 10), (wx - 20, 20), color=(.0, .0, .0, .8))

    def on_draw_overlay(self):
        text = html.escape(G.chat.text)
        if (round(time.time() - self.timer) % 2) == 1:
            self.update_text(text, G.chat.active_index)
        else:
            self.lable.text = "<font color='white'>"+text+"</font>"
        self.lable.draw()


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
        self.historyindex = -1
        self.active_index = -1
        self.CANCEL_INPUT = False
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:clear_chat", self.clear)

    def enter(self, text: str):
        """
        called when text is entered
        :param text: the text that is entered
        """
        self.text = self.text[:self.active_index+1] + text + self.text[self.active_index+1:]
        self.active_index += len(text)

    def on_key_press(self, symbol, modifiers):
        """
        called when an key is pressed
        :param symbol: the symbol that is pressed
        :param modifiers: the modifiers that are used
        """
        if symbol == 65288:  # BACK
            self.text = self.text[:self.active_index-1] + self.text[self.active_index:]
            self.active_index -= 1
        elif symbol == key.DELETE and self.active_index < len(self.text):
            self.text = self.text[:self.active_index] + self.text[self.active_index+1:]
        elif symbol == 65360: self.active_index = 0   # begin key
        elif symbol == key.END: self.active_index = len(self.text)
        elif symbol == key.ENTER:  # execute command
            self.CANCEL_INPUT = False
            G.eventhandler.call("chat:text_enter", self.text)
            logger.println("[CHAT][INFO] entered text: '{}'".format(self.text), write_into_console=False)
            if self.CANCEL_INPUT:
                self.history.insert(0, self.text)
                self.close()
                return
            if self.text.startswith("/"):
                # execute command
                G.commandparser.parse(self.text)
            else:
                self.print_ln(self.text)
            self.history.insert(0, self.text)
            self.close()
        elif symbol == key.UP and self.historyindex < len(self.history) - 1:  # go one item up in the history
            self.historyindex += 1
            self.text = self.history[self.historyindex]
            self.active_index = len(self.text)
        elif symbol == key.DOWN and self.historyindex >= 0:  # go one item down in the history
            self.historyindex -= 1
            if self.historyindex != -1:
                self.text = self.history[self.historyindex]
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
        # else:
            # print(symbol, modifiers)

    def print_ln(self, text: str):
        logger.println("[CHAT] {}".format(text))

    def close(self):
        """
        closes the chat
        """
        G.inventoryhandler.hide(G.world.get_active_player().inventories["chat"])
        self.active_index = 0

    def clear(self):
        self.history.clear()


G.chat = Chat()

