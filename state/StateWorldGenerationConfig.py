"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartTextInput
from .ui.UIPartTextInput import INT_PATTERN
import globals as G
import util.math
from pyglet.window import key
import pyglet
import random
import mod.ModMcpython
import state.StatePartConfigBackground


class StateWorldGenerationConfig(State.State):
    @staticmethod
    def get_name(): return "minecraft:world_generation_config"

    def __init__(self): State.State.__init__(self)

    def get_parts(self) -> list:
        parts = [UIPartButton.UIPartButton((300, 20), "#*gui.back*#", (-320, 20), anchor_window="MD",
                                           on_press=self.on_back_press),
                 UIPartButton.UIPartButton((300, 20), "#*multiplayer.status.finished*#", (20, 20), anchor_window="MD",
                                           on_press=self.on_generate_press),
                 UIPartButton.UIPartToggleButton((300, 20), ["#*special.value.true*#", "#*special.value.false*#"],
                                                 (-320, 150), anchor_window="MD",
                                                 text_constructor="#*special.worldgeneration.enable_auo_gen*#: {}"),
                 UIPartButton.UIPartToggleButton((300, 20), ["#*special.value.true*#", "#*special.value.false*#"],
                                                 (20, 150), anchor_window="MD",
                                                 text_constructor="#*special.worldgeneration.enable_barrier*#: {}")]
        text = [UIPartTextInput.UIPartTextInput((300, 40), (20, 50), anchor_window="MD",
                                                empty_overlay_text="#*special.worldgeneration.seed_empty*#"),
                UIPartTextInput.UIPartTextInput((300, 40), (-320, 50), anchor_window="MD",
                                                empty_overlay_text="#*special.worldgeneration.playername_empty*#"),
                UIPartTextInput.UIPartTextInput((300, 40), (-320, 100), anchor_window="MD", pattern=INT_PATTERN,
                                                empty_overlay_text="#*special.worldgeneration.worldsize|x|3*#"),
                UIPartTextInput.UIPartTextInput((300, 40), (20, 100), anchor_window="MD", pattern=INT_PATTERN,
                                                empty_overlay_text="#*special.worldgeneration.worldsize|y|3*#")]

        parts.append(UIPartTextInput.TextInputTabHandler([text[2], text[3], text[1], text[0]]))

        return parts + text + [state.StatePartConfigBackground.StatePartConfigBackground()]

    def on_back_press(self, x, y):
        G.statehandler.switch_to("minecraft:startmenu")

    def on_generate_press(self, x, y):
        G.world.cleanup(remove_dims=True)
        G.dimensionhandler.init_dims()
        sx = self.parts[7].entered_text; sx = 3 if sx == "" else int(sx)
        sy = self.parts[8].entered_text; sy = 3 if sy == "" else int(sy)
        G.worldgenerationhandler.enable_generation = True
        fx = sx // 2
        fy = sy // 2
        ffx = sx - fx
        ffy = sy - fy
        G.eventhandler.call("on_world_generation_prepared")
        seed = self.parts[5].entered_text
        if seed != "":
            try:
                seed = int(seed)
            except ValueError:
                seed = int.from_bytes(seed.encode("UTF-8"), "big")
        else:
            seed = random.randint(-100000, 100000)
        G.world.config["seed"] = seed
        G.eventhandler.call("on_world_generation_started")
        for cx in range(-fx, ffx):
            for cz in range(-fy, ffy):
                chunk = G.world.dimensions[0].get_chunk(cx, cz, generate=False)
                chunk.is_ready = False
                G.worldgenerationhandler.generate_chunk(chunk)
                chunk.is_ready = True
        G.eventhandler.call("on_game_generation_finished")
        G.window.position = (G.world.spawnpoint[0], util.math.get_max_y(G.world.spawnpoint), G.world.spawnpoint[1])
        G.world.config["enable_auto_gen"] = self.parts[2].textpages[self.parts[2].index] == "#*special.value.true*#"
        G.world.config["enable_world_barrier"] = \
            self.parts[3].textpages[self.parts[3].index] == "#*special.value.true*#"
        G.player.name = self.parts[6].entered_text
        if G.player.name == "": G.player.name = "unknown"
        G.statehandler.switch_to("minecraft:gameinfo")
        G.eventhandler.call("on_game_enter")

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_back_press(0, 0)
        elif symbol == key.ENTER:
            self.on_generate_press(0, 0)

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(1., 1., 1., 1.)

    def on_activate(self):
        for part in self.parts:
            if issubclass(type(part), UIPartTextInput.UIPartTextInput):
                part.reset()


worldgenerationconfig = None


def create():
    global worldgenerationconfig
    worldgenerationconfig = StateWorldGenerationConfig()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)

