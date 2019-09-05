"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import PIL.Image
import globals as G
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


def to_pyglet_image(image: PIL.Image.Image):
    image.save(G.local+"/tmp/imagehelper_topyglet.png")
    return pyglet.image.load(G.local+"/tmp/imagehelper_topyglet.png")


def to_pillow_image(image: pyglet.image.AbstractImage):
    image.save(G.local+"/tmp/imagehelper_topillow.png")
    return PIL.Image.open(G.local+"/tmp/imagehelper_topillow.png")


def to_pyglet_sprite(image: PIL.Image.Image):
    return pyglet.sprite.Sprite(to_pyglet_image(image))


