"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
# util functions from manipulating image data and converting between different formats
import PIL.Image
from mcpython import globals as G
import pyglet


def colorize(mask: PIL.Image.Image, color: tuple) -> PIL.Image.Image:
    """
    colorize an imagemask with an color
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
                colorp = (color[0] * color_alpha // 255, color[1] * color_alpha // 255,
                          color[2] * color_alpha // 255)
                new_image.putpixel((x, y), colorp)
    return new_image


def to_pyglet_image(image: PIL.Image.Image) -> pyglet.image.AbstractImage:
    """
    Will transform the image into an pyglet image
    :param image: the image to transform
    :return: the transformed one
    """
    image.save(G.tmp.name+"/imagehelper_topyglet.png")
    return pyglet.image.load(G.tmp.name+"/imagehelper_topyglet.png")


def to_pillow_image(image: pyglet.image.AbstractImage) -> PIL.Image.Image:
    """
    Will transform the pyglet image into an pillow one
    :param image: the image to transform
    :return: the transformed one
    """
    image.save(G.tmp.name+"/imagehelper_topillow.png")
    return PIL.Image.open(G.tmp.name+"/imagehelper_topillow.png")


def to_pyglet_sprite(image: PIL.Image.Image) -> pyglet.sprite.Sprite:
    """
    Will transform the pillow image into an pyglet sprite
    :param image: the image
    :return: the sprite
    """
    return pyglet.sprite.Sprite(to_pyglet_image(image))


