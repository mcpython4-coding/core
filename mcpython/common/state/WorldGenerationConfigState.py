"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import random

import mcpython.common.data.DataPacks
import mcpython.common.mod.ModMcpython
import mcpython.common.state.ConfigBackgroundPart
import mcpython.common.state.WorldGenerationProgressState
import mcpython.server.worldgen.noise.NoiseManager
import mcpython.util.math
from mcpython import shared
from pyglet.window import key

from . import AbstractState
from .ui import UIPartButton, UIPartTextInput
from .ui.UIPartTextInput import INT_PATTERN


class WorldGenerationConfig(AbstractState.AbstractState):
    NAME = "minecraft:world_generation_config"

    def __init__(self):
        AbstractState.AbstractState.__init__(self)

    def create_state_parts(self) -> list:
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
            UIPartButton.UIPartToggleButton(
                (300, 20),
                list(
                    mcpython.server.worldgen.noise.NoiseManager.manager.instances.keys()
                ),
                (-320, 240),
                anchor_window="MD",
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
            + [mcpython.common.state.ConfigBackgroundPart.ConfigBackground()]
        )

    def is_auto_gen_enabled(self) -> bool:
        return not bool(self.parts[2].index)

    def is_world_gen_barrier_enabled(self) -> bool:
        return not bool(self.parts[3].index)

    def get_world_config_name(self) -> str:
        return self.parts[4].text

    def get_seed(self) -> int:
        v = self.parts[7].entered_text
        if v != "":
            return hash(v)
        return random.randint(-1000000000000000000, 1000000000000000000)

    def get_player_name(self) -> str:
        v = self.parts[8].entered_text
        return "unknown" if v == "" else v

    def get_world_size(self):
        x = int(self.parts[9].entered_text) if self.parts[9].entered_text != "" else 3
        z = int(self.parts[10].entered_text) if self.parts[10].entered_text != "" else 3
        return x, z

    def get_seed_source(self):
        return self.parts[5].text

    async def on_back_press(self, x, y):
        await shared.state_handler.change_state("minecraft:start_menu")

    async def on_generate_press(self, x, y):
        filename = self.parts[11].entered_text
        if filename == "":
            filename = "New World"
        await shared.world.cleanup(remove_dims=True, filename=filename)
        await self.generate()

    async def generate(self):
        await shared.state_handler.states[
            "minecraft:world_generation"
        ].generate_from_user_input(self)

    def bind_to_eventbus(self):
        super().bind_to_eventbus()
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)

    async def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            await self.on_back_press(0, 0)
        elif symbol == key.ENTER:
            await self.on_generate_press(0, 0)

    async def activate(self):
        await super().activate()
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
            shared.world_generation_handler.configs["minecraft:overworld"].keys()
        )
        self.parts[4].update_text()


world_generation_config = None


async def create():
    global world_generation_config
    world_generation_config = WorldGenerationConfig()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create())
