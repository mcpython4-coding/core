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
import clipboard
import traceback


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
            text1 = text[:underline_index].replace("<", "&#60;").replace(">", "&#62;").replace("\\", "&#92;")
            text2 = text[underline_index].replace("<", "&#60;").replace(">", "&#62;").replace("\\", "&#92;")
            text3 = text[1+underline_index:].replace("<", "&#60;").replace(">", "&#62;").replace("\\", "&#92;")
            self.lable.text = "<font color='white'>"+text1+"<u>{}</u>".format(text2)+text3+"</font>"
        except IndexError:
            self.lable.text = text

    def on_activate(self):
        # print("opening chat")
        # traceback.print_stack()
        G.chat.text = ""
        G.chat.active_index = 0
        G.chat.has_entered_t = False
        self.eventbus.activate()

    def on_deactivate(self):
        # print("closing chat")
        # traceback.print_stack()
        self.eventbus.deactivate()

    def on_draw_background(self):
        wx, _ = G.window.get_size()
        util.opengl.draw_rectangle((10, 10), (wx - 20, 20), color=(.0, .0, .0))

    def on_draw_overlay(self):
        text = G.chat.text
        if (round(time.time() - self.timer) % 2) == 1:
            self.update_text(text, G.chat.active_index)
        else:
            self.lable.text = "<font color='white'>"+text.replace("<", "&#60").replace(">", "&#62").replace(
                "\\", "&#92")+"</font>"
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
        elif symbol == key.V and modifiers & key.MOD_CTRL:  # insert text from clipboard
            self.enter(clipboard.paste())

    def close(self):
        """
        closes the chat
        """
        G.inventoryhandler.hide(G.player.inventorys["chat"])
        self.active_index = 0


G.chat = Chat()

