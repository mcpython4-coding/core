"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
# util functions from manipulating image data and converting between different formats
import typing

import PIL.Image
from mcpython import shared
import pyglet


def colorize(mask: PIL.Image.Image, color: tuple) -> PIL.Image.Image:
    """
    colorize an image-mask (greyscale) with an color
    :param mask: the mask to base on
    :param color: the color to use
    :return: the colorized image
    """
    color = tuple(color)
    mask: PIL.Image.Image = mask.convert("L")
    new_image: PIL.Image.Image = PIL.Image.new("RGBA", mask.size)
    for x in range(mask.size[0]):
        for y in range(mask.size[1]):
            color_alpha = mask.getpixel((x, y))
            if color_alpha:
                pixel_color = (
                    color[0] * color_alpha // 255,
                    color[1] * color_alpha // 255,
                    color[2] * color_alpha // 255,
                )
                new_image.putpixel((x, y), pixel_color)
    return new_image


def to_pyglet_image(image: PIL.Image.Image) -> pyglet.image.AbstractImage:
    """
    Will transform the image into an pyglet image
    :param image: the image to transform
    :return: the transformed one
    todo: can we do this in-memory?
    """
    image.save(shared.tmp.name + "/image_helper_to_pyglet.png")
    return pyglet.image.load(shared.tmp.name + "/image_helper_to_pyglet.png")


def to_pillow_image(image: pyglet.image.AbstractImage) -> PIL.Image.Image:
    """
    Will transform the pyglet image into an pillow one
    :param image: the image to transform
    :return: the transformed one
    todo: can we do this in-memory?
    """
    image.save(shared.tmp.name + "/image_helper_to_pillow.png")
    return PIL.Image.open(shared.tmp.name + "/image_helper_to_pillow.png")


def to_pyglet_sprite(image: PIL.Image.Image) -> pyglet.sprite.Sprite:
    """
    Will transform the pillow image into an pyglet sprite
    :param image: the image
    :return: the sprite
    """
    return pyglet.sprite.Sprite(to_pyglet_image(image))


def hex_to_color(color: str) -> typing.Tuple[int, int, int]:
    return int(color[:2], base=16), int(color[2:4], base=16), int(color[4:6], base=16)
