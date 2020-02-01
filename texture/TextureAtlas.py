"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import PIL.Image
import ResourceLocator
import globals as G
import pyglet
import os
import mod.ModMcpython


MISSING_TEXTURE = ResourceLocator.read("assets/missingtexture.png", "pil").resize((64, 64))


class TextureAtlasGenerator:
    def __init__(self):
        self.atlases = [TextureAtlas()]

    def add_image(self, image: PIL.Image.Image) -> tuple:
        image = image.resize((64, 64), PIL.Image.NEAREST)
        for atlas in self.atlases:
            if image in atlas.images:
                return atlas.add_image(image), atlas
            elif len(atlas.images) < 16 ** 2:
                return atlas.add_image(image), atlas
        self.atlases.append(TextureAtlas())
        images = [image]
        for _ in range(3):
            images.append(images[-1].rotate(90))
        return tuple([self.atlases[-1].add_image(i) for i in images]), self.atlases[-1]

    def add_image_file(self, file: str) -> tuple:
        return self.add_image(ResourceLocator.read(file, "pil"))

    def add_images(self, images: list, one_atlased=True) -> list:
        if not one_atlased:
            return [self.add_image(x) for x in images]
        images = [image.resize((64, 64), PIL.Image.NEAREST) for image in images]
        rimages = []
        for image in images:
            r = [image]
            for _ in range(3):
                r.append(r[-1].rotate(90))
            rimages.append(r)
        for atlas in self.atlases:
            if atlas.is_free_for(rimages):
                return [([atlas.add_image(image) for image in imagel], atlas) for imagel in rimages]
        atlas = TextureAtlas()
        self.atlases.append(atlas)
        return [([atlas.add_image(image) for image in imagel], atlas) for imagel in rimages]

    def add_image_files(self, files: list, one_atlased=True) -> list:
        return self.add_images([ResourceLocator.read(x, "pil") for x in files], one_atlased=one_atlased)

    def output(self):
        os.makedirs(G.local+"/tmp/textureatlases")
        for i, atlas in enumerate(self.atlases):
            location = G.local+"/tmp/textureatlases/atlas_{}.png".format(i+1)
            atlas.texture.save(location)
            atlas.group = pyglet.graphics.TextureGroup(pyglet.image.load(location).get_texture())


class TextureAtlas:
    def __init__(self, size=(16, 16), image_size=(64, 64), add_missing_texture=True, pyglet_special_pos=True):
        self.size = size
        self.image_size = image_size
        self.pyglet_special_pos = pyglet_special_pos
        self.texture = PIL.Image.new("RGBA", (size[0] * image_size[0], size[1] * image_size[1]))
        self.next_index = (0, 0)
        self.images = []
        self.imagelocations = []  # an images[-parallel (x, y)-list
        if add_missing_texture: self.add_image(MISSING_TEXTURE)
        self.group = None

    def add_image(self, image: PIL.Image.Image, ind=None) -> tuple:
        if ind is None: ind = image
        if ind in self.images: return self.imagelocations[self.images.index(ind)]
        self.images.append(ind)
        x, y = self.next_index
        self.texture.paste(image, (x*self.image_size[0], (self.size[1]-y-1 if self.pyglet_special_pos else y) *
                                   self.image_size[1]))
        pos = x, y
        x += 1
        if x >= self.size[0]: x = 0; y += 1
        self.next_index = (x, y)
        self.imagelocations.append(pos)
        return pos

    def is_free_for(self, images: list) -> bool:
        count = 0
        for image in images:
            if image not in self.images: count += 1
        return count <= self.size[0] * self.size[1] - len(self.images)


handler = TextureAtlasGenerator()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:textureatlas:bake", handler.output,
                                            info="building texture atlases...")

