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
# util functions from manipulating image data and converting between different formats
import typing

import deprecation
import PIL.Image
from mcpython import shared


def colorize(
    mask: PIL.Image.Image,
    color: tuple,
    colorizer=lambda color, mask: tuple(c * mask // 255 for c in color[:3])
    + (tuple() if len(color) == 3 else (color[-1])),
) -> PIL.Image.Image:
    """
    Colorize an image-mask with a color using colorizer as the operator
    :param mask: the mask to base on
    :param color: the color to use
    :param colorizer: the colorizer method to use, defaults to a simple channel-based multiplication
    :return: the colorized image
    """
    color = tuple(color)
    mask: PIL.Image.Image = mask.convert("L")
    new_image: PIL.Image.Image = PIL.Image.new("RGBA", mask.size)
    for x in range(mask.size[0]):
        for y in range(mask.size[1]):
            color_alpha = mask.getpixel((x, y))
            if color_alpha:
                pixel_color = colorizer(color, color_alpha)
                new_image.putpixel((x, y), pixel_color)
    return new_image


def layer_with_alpha(base: PIL.Image.Image, top: PIL.Image.Image):
    top = top.convert("RGBA")
    new_image: PIL.Image.Image = PIL.Image.new("RGBA", base.size)
    for x in range(base.size[0]):
        for y in range(base.size[1]):
            b = base.getpixel((x, y))
            t = top.getpixel((x, y))
            a = t[3] / 255
            if a == 0:
                new_image.putpixel((x, y), b)
            else:
                new_image.putpixel(
                    (x, y),
                    tuple(round(e[0] * (1 - a) + e[1] * a) for e in zip(b, t[:3])),
                )

    return new_image


def to_pyglet_image(image: PIL.Image.Image):
    """
    Will transform the image into an pyglet image
    :param image: the image to transform
    :return: the transformed one
    todo: can we do this in-memory? (less time consumed)
    """
    import pyglet

    image.save(shared.tmp.name + "/image_helper_to_pyglet.png")
    return pyglet.image.load(shared.tmp.name + "/image_helper_to_pyglet.png")


def to_pyglet_sprite(image: PIL.Image.Image):
    """
    Will transform the pillow image into an pyglet sprite
    :param image: the image
    :return: the sprite
    """
    import pyglet

    return pyglet.sprite.Sprite(to_pyglet_image(image))


def to_pillow_image(image) -> PIL.Image.Image:
    """
    Will transform the pyglet image into an pillow one
    :param image: the image to transform
    :return: the transformed one
    todo: can we do this in-memory? (less time consumed)
    """
    import pyglet

    image.save(shared.tmp.name + "/image_helper_to_pillow.png")
    return PIL.Image.open(shared.tmp.name + "/image_helper_to_pillow.png")


def hex_to_color(color: str) -> typing.Tuple[int, int, int]:
    """
    Helper method for transforming a hex string encoding a color into a tuple of color entries
    """
    return int(color[:2], base=16), int(color[2:4], base=16), int(color[4:6], base=16)


def int_hex_to_color(color: int) -> typing.Tuple[int, int, int]:
    v = hex(color)[2:]
    return hex_to_color("0" * (6 - len(v)) + v)


@deprecation.deprecated()
def resize_image_pyglet(image, size: typing.Tuple[int, int]):
    return to_pyglet_image(to_pillow_image(image).resize(size, PIL.Image.NEAREST))
