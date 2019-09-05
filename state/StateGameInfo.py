"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import state.State
import state.StatePartGame
from state.ui import UIPartButton, UIPartImage, UIPartLable
import util.texture
import ResourceLocator
from pyglet.window import key, mouse


sprite = util.texture.to_pyglet_sprite(ResourceLocator.read("gui/demo_background", mode="pil").crop((0, 0, 248, 166)))


class StateGameInfo(state.State.State):
    @staticmethod
    def get_name():
        return "minecraft:gameinfo"

    @staticmethod
    def is_mouse_exclusive():
        return False

    def __init__(self):
        state.State.State.__init__(self)

    def get_parts(self) -> list:
        return [state.StatePartGame.StatePartGame(activate_physics=False, activate_mouse=False,
                                                  activate_keyboard=False, activate_focused_block=False),
                UIPartImage.UIPartLable(sprite, (0, 0), anchor_window="MM", anchor_lable="MM"),
                UIPartLable.UIPartLable("These Game is written", (0, 40), anchor_lable="MM", anchor_window="MM",
                                        text_size=10),
                UIPartLable.UIPartLable("completely in python", (0, 30), anchor_lable="MM", anchor_window="MM",
                                        text_size=10),
                UIPartLable.UIPartLable("DO NOT REPORT ANY BUG",
                                        (0, 15), anchor_lable="MM", anchor_window="MM", text_size=10),
                UIPartLable.UIPartLable("TO THE MOJANG BUG TRACKER.",
                                        (0, 5), anchor_lable="MM", anchor_window="MM", text_size=10),
                UIPartLable.UIPartLable("GO TO THE BUG TRACKER",
                                        (0, -10), anchor_lable="MM", anchor_window="MM", text_size=10),
                UIPartLable.UIPartLable("OF THE GITHUB PROJECT",
                                        (0, -20), anchor_lable="MM", anchor_window="MM", text_size=10)]

    def get_event_functions(self) -> list:
        return [(self.on_key_press, "user:keyboard:press"),
                (self.on_mouse_press, "user:mouse:press")]

    def on_activate(self, old):
        pass

    def on_deactivate(self, new):
        pass

    @G.eventhandler("user:keyboard:press", callactive=False)
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            G.statehandler.switch_to("minecraft:game")

    @G.eventhandler("user:mouse:press", callactive=False)
    def on_mouse_press(self, x, y, button, modifiers):
        G.statehandler.switch_to("minecraft:game")


gameinfo = StateGameInfo()

