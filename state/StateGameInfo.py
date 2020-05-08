"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import state.State
import state.StatePartGame
from state.ui import UIPartButton, UIPartImage, UIPartLable
import util.texture
import ResourceLocator
from pyglet.window import key, mouse
import mod.ModMcpython


# todo: use pyglet.image.Image.get_region(area)
sprite = util.texture.to_pyglet_sprite(ResourceLocator.read("gui/demo_background", mode="pil").crop((0, 0, 248, 166)))


class StateGameInfo(state.State.State):
    NAME = "minecraft:gameinfo"

    @staticmethod
    def is_mouse_exclusive(): return False

    def __init__(self): state.State.State.__init__(self)

    def get_parts(self) -> list:
        parts = [state.StatePartGame.StatePartGame(activate_physics=False, activate_mouse=False,
                                                   activate_keyboard=False, activate_focused_block=False),
                 UIPartImage.UIPartImage(sprite, (0, 0), anchor_window="MM", anchor_image="MM")]
        y = 40
        for i in range(7):
            parts.append(UIPartLable.UIPartLable("#*special.gameinfo.line{}*#".format(i+1),
                                                 (0, y), anchor_lable="MM", anchor_window="MM", text_size=10))
            y -= 12
        return parts

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("user:mouse:press", self.on_mouse_press)

    @staticmethod
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE or symbol == key.E:
            G.statehandler.switch_to("minecraft:game", immediate=False)

    @staticmethod
    def on_mouse_press(x, y, button, modifiers):
        G.statehandler.switch_to("minecraft:game", immediate=False)


gameinfo = None


def create():
    global gameinfo
    gameinfo = StateGameInfo()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

