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


class ChatInventory(gui.Inventory.Inventory):
    """
    main class for chat
    """

    def on_create(self):
        self.lable = pyglet.text.Label(x=15, y=15)
        self.enable_blink = True
        self.blink_state = True
        self.blink_start = time.time()

    def on_activate(self):
        G.chat.text = ""
        G.chat.has_entered_t = False
        G.eventhandler.activate_to_callback("user:keyboard:press", G.chat.on_key_press)
        G.eventhandler.activate_to_callback("user:keyboard:enter", G.chat.enter)

    def on_deactivate(self):
        G.eventhandler.deactivate_from_callback("user:keyboard:press", G.chat.on_key_press)
        G.eventhandler.deactivate_from_callback("user:keyboard:enter", G.chat.enter)

    def on_draw_background(self):
        if time.time() - self.blink_start > 0.5:
            self.blink_state = not self.blink_state
            self.blink_start = time.time()
        wx, _ = G.window.get_size()
        util.opengl.draw_rectangle((10, 10), (wx - 20, 20), color=(.0, .0, .0))

    def on_draw_overlay(self):
        wx, _ = G.window.get_size()
        self.lable.text = G.chat.text
        self.lable.text += " " if not self.blink_state else "_"
        while self.lable.content_width > wx - 20: self.lable.text = self.lable.text[1:]
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
        self.has_entered_t = False

    def enter(self, text: str):
        """
        callen when text is entered
        :param text: the text that is entered
        """
        if not self.has_entered_t and text == "t":  # check for t at beginning -> work-around after chat opening
            self.has_entered_t = True
            return
        self.text += text

    def on_key_press(self, symbol, modifiers):
        """
        callen when an key is pressed
        :param symbol: the symbol that is pressed
        :param modifiers: the modifiers that are used
        """
        if symbol == 65288:  # BACK
            self.text = self.text[:-1]
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
        elif symbol == key.DOWN and self.historyindex >= 0:  # go one item down in the history
            self.historyindex -= 1
            if self.historyindex != -1:
                self.text = self.history[self.historyindex]
            else:
                self.text = ""

    def close(self):
        """
        closes the chat
        """
        G.inventoryhandler.hide(G.player.inventorys["chat"])


G.chat = Chat()

