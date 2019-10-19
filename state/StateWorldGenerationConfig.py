"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
from . import State, StatePartGame
from .ui import UIPartButton, UIPartTextInput
from .ui.UIPartTextInput import INT_PATTERN
import globals as G
import util.math
from pyglet.window import key
import pyglet
import random


class StateWorldGenerationConfig(State.State):
    @staticmethod
    def get_name(): return "minecraft:world_generation_config"

    def __init__(self): State.State.__init__(self)

    def get_parts(self) -> list:
        return [UIPartButton.UIPartButton((300, 20), "#*gui.back*#", (-320, 20), anchor_window="MD",
                                          on_press=self.on_back_press),
                UIPartButton.UIPartButton((300, 20), "#*multiplayer.status.finished*#", (20, 20), anchor_window="MD",
                                          on_press=self.on_generate_press),
                UIPartTextInput.UIPartTextInput((300, 40), (20, 50), anchor_window="MD",
                                                empty_overlay_text="#*special.worldgeneration.seed_empty*#"),
                UIPartTextInput.UIPartTextInput((300, 40), (-320, 50), anchor_window="MD",
                                                empty_overlay_text="#*special.worldgeneration.playername_empty*#"),
                UIPartTextInput.UIPartTextInput((300, 40), (-320, 100), anchor_window="MD", pattern=INT_PATTERN,
                                                empty_overlay_text="#*special.worldgeneration.worldsize|x|3*#"),
                UIPartTextInput.UIPartTextInput((300, 40), (20, 100), anchor_window="MD", pattern=INT_PATTERN,
                                                empty_overlay_text="#*special.worldgeneration.worldsize|y|3*#"),
                UIPartButton.UIPartToggleButton((300, 20), ["#*special.value.true*#", "#*special.value.false*#"],
                                                (-320, 150), anchor_window="MD",
                                                text_constructor="#*special.worldgeneration.enable_auo_gen*#: {}"),
                UIPartButton.UIPartToggleButton((300, 20), ["#*special.value.true*#", "#*special.value.false*#"],
                                                (20, 150), anchor_window="MD",
                                                text_constructor="#*special.worldgeneration.enable_barrier*#: {}")]

    def on_back_press(self, x, y):
        G.statehandler.switch_to("minecraft:startmenu")

    def on_generate_press(self, x, y):
        G.world.cleanup(remove_dims=True)
        G.world.add_dimension(0, {"configname": "default_overworld"})
        sx = self.parts[4].entered_text; sx = 3 if sx == "" else int(sx)
        sy = self.parts[4].entered_text; sy = 3 if sy == "" else int(sy)
        G.worldgenerationhandler.enable_generation = True
        fx = sx // 2
        fy = sy // 2
        ffx = sx - fx
        ffy = sy - fy
        for cx in range(-fx, ffx):
            for cz in range(-fy, ffy):
                chunk = G.world.dimensions[0].get_chunk(cx, cz, generate=False)
                chunk.is_ready = False
                G.worldgenerationhandler.generate_chunk(chunk)
                chunk.is_ready = True
        G.window.position = (0, util.math.get_max_y((0, 0, 0)), 0)
        G.world.config["enable_auto_gen"] = self.parts[6].textpages[self.parts[6].index] == "#*special.value.true*#"
        G.world.config["enable_world_barrier"] = \
            self.parts[7].textpages[self.parts[7].index] == "#*special.value.true*#"
        G.player.name = self.parts[3].entered_text
        if G.player.name == "": G.player.name = "unknown"
        seed = self.parts[2].entered_text
        if seed != "":
            try:
                seed = int(seed)
            except ValueError:
                seed = int.from_bytes(seed.encode("UTF-8"), "big")
        else:
            seed = random.randint(-100000, 100000)
        G.world.config["seed"] = seed
        G.statehandler.switch_to("minecraft:gameinfo")

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("render:draw:2d:background", self.on_draw_2d_pre)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.on_back_press(0, 0)

    @staticmethod
    def on_draw_2d_pre():
        pyglet.gl.glClearColor(1., 1., 1., 1.)

    def on_activate(self):
        for part in self.parts:
            if issubclass(type(part), UIPartTextInput.UIPartTextInput):
                part.reset()


escape = StateWorldGenerationConfig()

