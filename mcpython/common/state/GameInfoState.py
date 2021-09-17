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
import mcpython.common.state.AbstractState
import mcpython.common.state.GameViewStatePart
import mcpython.common.mod.ModMcpython
import mcpython.engine.ResourceLoader
import mcpython.util.texture
from mcpython import shared
from mcpython.common.state.ui import UIPartLabel
from mcpython.common.state.ui import UIPartImage
from mcpython.util.annotation import onlyInClient
from pyglet.window import key

# todo: use pyglet.image.Image.get_region(area)
sprite = mcpython.util.texture.to_pyglet_sprite(
    mcpython.engine.ResourceLoader.read_image("gui/demo_background").crop(
        (0, 0, 248, 166)
    )
)


@onlyInClient()
class GameInfo(mcpython.common.state.AbstractState.AbstractState):
    NAME = "minecraft:game_info"

    @staticmethod
    def is_mouse_exclusive():
        return False

    def activate(self):
        super().activate()

        if not shared.IS_CLIENT:
            shared.state_handler.change_state("minecraft:game", immediate=False)

    def get_parts(self) -> list:
        parts = [
            mcpython.common.state.GameViewStatePart.GameView(
                activate_physics=False,
                activate_mouse=False,
                activate_keyboard=False,
                activate_focused_block=False,
            ),
            UIPartImage.UIPartImage(
                sprite, (0, 0), anchor_window="MM", anchor_image="MM"
            ),
        ]
        y = 40
        for i in range(7):
            parts.append(
                UIPartLabel.UIPartLabel(
                    "#*special.gameinfo.line{}*#".format(i + 1),
                    (0, y),
                    anchor_lable="MM",
                    anchor_window="MM",
                    text_size=10,
                )
            )
            y -= 12
        return parts

    def bind_to_eventbus(self):
        self.eventbus.subscribe("user:keyboard:press", self.on_key_press)
        self.eventbus.subscribe("user:mouse:press", self.on_mouse_press)

    @staticmethod
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE or symbol == key.E:
            shared.state_handler.change_state("minecraft:game", immediate=False)

    @staticmethod
    def on_mouse_press(x, y, button, modifiers):
        shared.state_handler.change_state("minecraft:game", immediate=False)


game_info = None


@onlyInClient()
def create():
    global game_info
    game_info = GameInfo()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe("stage:states", create)
