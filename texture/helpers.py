"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
try:
    import PIL.Image
except ImportError:
    raise RuntimeError("can't load PIL, pillow seems to be not installed. Please install it") from None
import os
import globals as G
import pyglet
import ResourceLocator


def load_image(location) -> PIL.Image.Image:
    resource = ResourceLocator.ResourceLocator(location)
    if resource and resource.data:
        return resource.data
    if not os.path.exists(location): location = G.local+"/"+location
    return PIL.Image.open(location)


def resize_image(image: PIL.Image.Image, size) -> PIL.Image.Image:
    return image.resize(size)


def get_image_part(image: PIL.Image.Image, area) -> PIL.Image.Image:
    return image.crop(area)


def to_pyglet_image(image: PIL.Image.Image):
    image.save(G.local+"/tmp/imagehelper_topyglet.png")
    return pyglet.image.load(G.local+"/tmp/imagehelper_topyglet.png")


def to_pillow_image(image: pyglet.image.AbstractImage):
    image.save(G.local+"/tmp/imagehelper_topillow.png")
    return PIL.Image.open(G.local+"/tmp/imagehelper_topillow.png")


def to_pyglet_sprite(image: PIL.Image.Image):
    return pyglet.sprite.Sprite(to_pyglet_image(image))

