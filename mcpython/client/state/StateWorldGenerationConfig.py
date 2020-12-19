"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import random

from . import State
from .ui import UIPartButton, UIPartTextInput
from .ui.UIPartTextInput import INT_PATTERN
from mcpython import shared as G
import mcpython.util.math
from pyglet.window import key
import pyglet
import mcpython.common.mod.ModMcpython
import mcpython.client.state.StatePartConfigBackground
import mcpython.common.DataPack
import mcpython.client.state.StateWorldGeneration
from mcpython.util.annotation import onlyInClient


@onlyInClient()
class StateWorldGenerationConfig(State.State):
    NAME = "minecraft:world_generation_config"

    def __init__(self):
        State.State.__init__(self)

    def get_parts(self) -> list:
        parts = [
            UIPartButton.UIPartButton(
                (300, 20),
                "#*gui.back*#",
                (-320, 20),
                anchor_window="MD",
                on_press=self.on_back_press,
            ),
            UIPartButton.UIPartButton(
                (300, 20),
                "#*multiplayer.status.finished*#",
                (20, 20),
                anchor_window="MD",
                on_press=self.on_generate_press,
            ),
            UIPartButton.UIPartToggleButton(
                (300, 20),
                ["#*special.value.true*#", "#*special.value.false*#"],
                (-320, 200),
                anchor_window="MD",
                text_constructor="#*special.worldgeneration.enable_auo_gen*#: {}",
            ),
            UIPartButton.UIPartToggleButton(
                (300, 20),
                ["#*special.value.true*#", "#*special.value.false*#"],
                (20, 200),
                anchor_window="MD",
                text_constructor="#*special.worldgeneration.enable_barrier*#: {}",
            ),
            UIPartButton.UIPartToggleButton(
                (300, 20), ["default"], (20, 240), anchor_window="MD"
            ),
        ]
        text = [
            UIPartTextInput.UIPartTextInput(
                (300, 40),
                (20, 50),
                anchor_window="MD",
                empty_overlay_text="#*special.worldgeneration.seed_empty*#",
            ),
            UIPartTextInput.UIPartTextInput(
                (300, 40),
                (-320, 50),
                anchor_window="MD",
                empty_overlay_text="#*special.worldgeneration.playername_empty*#",
            ),
            UIPartTextInput.UIPartTextInput(
                (300, 40),
                (-320, 100),
                anchor_window="MD",
                pattern=INT_PATTERN,
                empty_overlay_text="#*special.worldgeneration.worldsize|x|3*#",
            ),
            UIPartTextInput.UIPartTextInput(
                (300, 40),
                (20, 100),
                anchor_window="MD",
                pattern=INT_PATTERN,
                empty_overlay_text="#*special.worldgeneration.worldsize|y|3*#",
            ),
            UIPartTextInput.UIPartTextInput(
                (640, 40),
                (0, 170),
                anchor_window="MD",
                anchor_ti="MM",
                empty_overlay_text="World Name",
            ),
        ]

        parts.append(
            UIPartTextInput.TextInputTabHandler([text[2], text[3], text[1], text[0]])
        )

        return (
            parts
            + text
            + [
                mcpython.client.state.StatePartConfigBackground.StatePartConfigBackground()
            ]
        )

    def is_auto_gen_enabled(self) -> bool:
        return not bool(self.parts[2].index)

    def is_world_gen_barrier_enabled(self) -> bool:
        return not bool(self.parts[3].index)

    def get_world_config_name(self) -> str:
        return self.parts[4].text

    def get_seed(self) -> int:
        v = self.parts[6].entered_text
        if v != "":
            return hash(v)
        return random.randint(-1000000000000000000, 1000000000000000000)

    def get_player_name(self) -> str:
        v = self.parts[7].entered_text
        return "unknown" if v == "" else v

    def get_world_size(self):
        x = int(self.parts[8].entered_text) if self.parts[8].entered_text != "" else 3
        z = int(self.parts[9].entered_text) if self.parts[9].entered_text != "" else 3
        return x, z

    def on_back_press(self, x, y):
        G.state_handler.switch_to("minecraft:startmenu")

    def on_generate_press(self, x, y):
        filename = self.parts[9].entered_text
        if filename == "":
            filename = "New World"
        G.world.cleanup(remove_dims=True, filename=filename)
        self.generate()

    def generate(self):
        G.state_handler.switch_to("minecraft:world_generation")

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
        pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)

    def activate(self):
        super().activate()
        for part in self.parts:
            if issubclass(type(part), UIPartTextInput.UIPartTextInput):
                part.reset()
        for part in self.parts[6:10]:
            part.index = 0
            part.text = ""

        for part in self.parts[2:5]:
            part.index = 0
            part.update_text()

        self.parts[4].text_pages = list(
            G.world_generation_handler.configs["minecraft:overworld"].keys()
        )
        self.parts[4].update_text()


world_generation_config = None


@onlyInClient()
def create():
    global world_generation_config
    world_generation_config = StateWorldGenerationConfig()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
