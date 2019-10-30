"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import gui.Inventory
import util.opengl
import pyglet
from pyglet.window import key
import time
import chat.command.CommandHandler
import event.EventHandler
import event.EventBus


class ChatInventory(gui.Inventory.Inventory):
    """
    main class for chat
    """

    def on_create(self):
        self.lable = pyglet.text.HTMLLabel("", x=15, y=15)
        self.enable_blink = True
        self.timer = time.time()
        self.eventbus = G.eventhandler.create_bus()
        self.eventbus.subscribe("user:keyboard:press", G.chat.on_key_press)
        self.eventbus.subscribe("user:keyboard:enter", G.chat.enter)

    def update_text(self, text, underline_index):
        if len(text) <= underline_index: text += "_"
        if len(text) <= underline_index:
            self.lable.text = text
            return
        try:
            self.lable.text = "<font color='white'>"+text[:underline_index]+"<u>{}</u>".format(
                text[underline_index])+text[1+underline_index:]+"</font>"
        except IndexError:
            self.lable.text = text

    def on_activate(self):
        G.chat.text = ""
        G.chat.active_index = 0
        G.chat.has_entered_t = False
        self.eventbus.activate()

    def on_deactivate(self):
        self.eventbus.deactivate()

    def on_draw_background(self):
        wx, _ = G.window.get_size()
        util.opengl.draw_rectangle((10, 10), (wx - 20, 20), color=(.0, .0, .0))

    def on_draw_overlay(self):
        if (round(time.time() - self.timer) % 2) == 1:
            self.update_text(G.chat.text, G.chat.active_index)
        else:
            self.lable.text = "<font color='white'>"+G.chat.text+"</font>"
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
        self.active_index = 0

    def enter(self, text: str):
        """
        callen when text is entered
        :param text: the text that is entered
        """
        if text == "<":
            text = "&#60"
        if text == ">":
            text = "&#63"
        if self.text != "":
            self.text = self.text[:self.active_index+1] + text + self.text[self.active_index+1:]
        else:
            self.text = text
        self.active_index += len(text)

    def on_key_press(self, symbol, modifiers):
        """
        callen when an key is pressed
        :param symbol: the symbol that is pressed
        :param modifiers: the modifiers that are used
        """
        if symbol == 65288:  # BACK
            self.text = self.text[:self.active_index] + self.text[self.active_index+1:]
            self.active_index -= 1
        elif symbol == key.ENTER:  # execute command
            if self.text.startswith("/"):
                # excute command
                G.commandparser.parse(self.text)
            else:
                print("[CHAT] {}".format(self.text))
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
        elif symbol == key.LEFT and self.active_index > 0: self.active_index -= 1
        elif symbol == key.RIGHT and self.active_index < len(self.text): self.active_index += 1

    def close(self):
        """
        closes the chat
        """
        G.inventoryhandler.hide(G.player.inventorys["chat"])
        self.active_index = 0


G.chat = Chat()

