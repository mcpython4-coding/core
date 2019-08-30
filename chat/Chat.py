"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import gui.Inventory
import util.opengl
import pyglet
from pyglet.window import key
import json
import time
import chat.command.CommandHandler


class ChatInventory(gui.Inventory.Inventory):
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
    def __init__(self):
        self.text: str = ""
        self.history: list = []
        self.historyindex = -1
        self.has_entered_t = False

    @staticmethod
    def key_to_value(symbol, modifiers, table) -> str or None:
        for keye in table.keys():
            if str(symbol) == keye or (hasattr(key, keye) and getattr(key, keye) == symbol):
                for modifiergroup in table[keye]:
                    if len(modifiergroup["modifier"]) == 0 and modifiers == 0:
                        return modifiergroup["value"]
                    flag = True
                    for modifier in modifiergroup["modifier"]:
                        if not (type(modifier) == int and modifiers & modifier) and not (hasattr(key, modifier) and
                                                                                modifiers & getattr(key, modifier)):
                            flag = False
                    if flag:
                        return modifiergroup["value"]

    def enter(self, text: str):
        if not self.has_entered_t and text == "t":
            self.has_entered_t = True
            return
        self.text += text

    def on_key_press(self, symbol, modifiers):
        if symbol == 65288:  # BACK
            self.text = self.text[:-1]
        elif symbol == key.ENTER:
            if self.text.startswith("/"):
                # excute command
                G.commandparser.parse(self.text)
            else:
                print("[CHAT] {}".format(self.text))
            self.history = [self.text] + self.history
            self.close()
        elif symbol == key.UP and self.historyindex < len(self.history) - 1:
            self.historyindex += 1
            self.text = self.history[self.historyindex]
        elif symbol == key.DOWN and self.historyindex >= 0:
            self.historyindex -= 1
            if self.historyindex != -1:
                self.text = self.history[self.historyindex]
            else:
                self.text = ""

    def close(self):
        G.inventoryhandler.hide(G.player.inventorys["chat"])


G.chat = Chat()

