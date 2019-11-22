"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import PIL.Image
from collections import Counter
import math
import os
import util.math


os.makedirs(G.local+"/tmp/textureatlases")


class TextureAtlas:
    def __init__(self, image_table_count, image_size, base_color=(0, 0, 0, 0)):
        self.image = PIL.Image.new("RGBA", [round(image_table_count[i] * image_size[i]) for i in range(2)], base_color)
        self.image_table_count = image_table_count
        self.image_size = image_size
        self.images = []
        self.imagepositions = []
        self.next_image_index = -1, 0

    def add_image(self, image: PIL.Image.Image) -> tuple:
        if image in self.images:
            return self.imagepositions[self.images.index(image)]
        sx, sy = self.image_size
        cx, cy = self.image_table_count
        x, y = self.next_image_index
        x += 1
        if x >= cx:
            x = 0
            y += 1
        if y >= cy: raise ValueError("unsupported operation on texture atlas. texture atlas is full")
        px, py = x * sx, y * sy
        try:
            self.image.paste(image, (px, py))
        except OSError: pass
        self.images.append(image)
        self.imagepositions.append((x, y))
        self.next_image_index = (x, y)
        return x, y


class TextureAtlasReference:
    def __init__(self, atlas):
        self.atlas = atlas
        self.position = None


class TextureAtlasReferenceList:
    def __init__(self, atlas):
        self.atlas = atlas
        self.array = None


class BlockTextureAtlas:
    """
    base class for an block texture atlas based on mod name
    todo: make prebuilded & load from index file
    """

    def __init__(self, modname, max_image_size=(64, 64)):
        self.max_image_size = max_image_size
        self.modname = modname
        self.atlas = None
        self.images = []
        self.imagerefs = []

    def add_image(self, image: PIL.Image.Image) -> TextureAtlasReference:
        if image in self.images: return self.imagerefs[self.images.index(image)]
        s = image.size[0]
        if s > self.max_image_size[0] or s > self.max_image_size[1]: self.max_image_size = (s, s)
        reference = TextureAtlasReference(self)
        self.images.append(image)
        self.imagerefs.append(reference)
        return reference

    def add_image_array(self, images: list) -> TextureAtlasReferenceList:
        reference = TextureAtlasReferenceList(self)
        reference.array = [self.add_image(i) for i in images]
        return reference

    def finish(self):
        s = len(self.images)
        m = util.math.next_power_of_2(round(math.sqrt(s) + 1))
        self.atlas = TextureAtlas((m, m), self.max_image_size)
        for i, image in enumerate(self.images):
            try:
                self.imagerefs[i].position = self.atlas.add_image(image.resize(self.max_image_size))
            except OSError:
                print("[TEXTUREATLAS][ERROR] OSError during trying to add image")
        self.atlas.image.save(G.local+"/tmp/textureatlases/atlas_{}.png".format(self.modname))

