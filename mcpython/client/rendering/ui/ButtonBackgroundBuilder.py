import math

import mcpython.ResourceLoader
from mcpython.util import texture as texture_util
import pyglet
import PIL.Image
import enum


class ButtonState(enum.Enum):
    ACTIVE = 0
    HOVERING = 1
    DISABLED = 2


class ButtonBackgroundBuilder:
    def __init__(self, texture_default: PIL.Image.Image, texture_hovering: PIL.Image.Image, texture_disabled: PIL.Image.Image):
        self.texture_default = texture_default
        self.texture_hovering = texture_hovering
        self.texture_disabled = texture_disabled

    def get_texture_for_state(self, state: ButtonState) -> PIL.Image.Image:
        if state == ButtonState.ACTIVE:
            return self.texture_default
        elif state == ButtonState.HOVERING:
            return self.texture_hovering
        elif state == ButtonState.DISABLED:
            return self.texture_disabled
        raise ValueError(state)
        
    def get_texture_for_size(self, sx: int, sy: int, state: ButtonState) -> PIL.Image.Image:
        texture = self.get_texture_for_state(state)
        ox, oy = texture.size
        new = PIL.Image.new("RGBA", (sx, sy))

        # Corners
        new.paste(texture.crop((0, 0, 8, 8)))
        new.paste(texture.crop((ox - 8, 0, ox, 8)), (sx - 8, 0))
        new.paste(texture.crop((0, oy - 8, 8, oy)), (0, sy - 8))
        new.paste(texture.crop((ox - 8, oy - 8, ox, oy)), (sx - 8, sy - 8))

        return new

    def get_pyglet_texture(self, sx: int, sy: int, state: ButtonState) -> pyglet.image.AbstractImage:
        return texture_util.to_pyglet_image(self.get_texture_for_size(sx, sy, state))


WIDGETS = mcpython.ResourceLoader.read_image("assets/minecraft/textures/gui/widgets.png")
DefaultButtonTexture = ButtonBackgroundBuilder(
    WIDGETS.crop((2, 256 - 66 - 17, 196 + 2, 14 + 256 - 66 - 17)),
    WIDGETS.crop((2, 256 - 86 - 17, 196 + 2, 14 + 256 - 86 - 17)),
    WIDGETS.crop((2, 256 - 46 - 17, 196+2, 14 + 256 - 46 - 17))
)

