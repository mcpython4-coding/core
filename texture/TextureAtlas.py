"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import PIL.Image
import ResourceLocator
import globals as G
import pyglet
import os


MISSING_TEXTURE = ResourceLocator.read("assets/missingtexture.png", "pil").resize((64, 64))


class TextureAtlasGenerator:
    def __init__(self):
        self.atlases = [TextureAtlas()]

    def add_image(self, image: PIL.Image.Image) -> tuple:
        image = image.resize((64, 64))
        for atlas in self.atlases:
            if image in atlas.images:
                return atlas.add_image(image), atlas
            elif len(atlas.images) < 16 ** 2:
                return atlas.add_image(image), atlas
        self.atlases.append(TextureAtlas())
        return self.atlases[-1].add_image(image), self.atlases[-1]

    def add_image_file(self, file: str) -> tuple:
        return self.add_image(ResourceLocator.read(file, "pil"))

    def add_images(self, images: list, one_atlased=True) -> list:
        if not one_atlased:
            return [self.add_image(x) for x in images]
        images = [image.resize((64, 64)) for image in images]
        for atlas in self.atlases:
            if atlas.is_free_for(images):
                return [(atlas.add_image(image), atlas) for image in images]
        atlas = TextureAtlas()
        self.atlases.append(atlas)
        return [(atlas.add_image(image), atlas) for image in images]

    def add_image_files(self, files: list, one_atlased=True) -> list:
        return self.add_images([ResourceLocator.read(x, "pil") for x in files], one_atlased=one_atlased)

    def output(self):
        os.makedirs(G.local+"/tmp/textureatlases")
        for i, atlas in enumerate(self.atlases):
            location = G.local+"/tmp/textureatlases/atlas_{}.png".format(i+1)
            atlas.texture.save(location)
            atlas.group = pyglet.graphics.TextureGroup(pyglet.image.load(location).get_texture())


class TextureAtlas:
    def __init__(self, size=(16*64, 16*64)):
        self.texture = PIL.Image.new("RGBA", size)
        self.next_index = (0, 0)
        self.images = []
        self.imagelocations = []  # an image[-parallel (x, y)-list
        self.add_image(MISSING_TEXTURE)
        self.group = None

    def add_image(self, image: PIL.Image.Image) -> tuple:
        if image in self.images: return self.imagelocations[self.images.index(image)]
        self.images.append(image)
        x, y = self.next_index
        self.texture.paste(image, (x*64, (15-y) * 64))
        pos = x, y
        x += 1
        if x >= 16: x = 0; y += 1
        self.next_index = (x, y)
        self.imagelocations.append(pos)
        return pos

    def is_free_for(self, images: list) -> bool:
        count = 0
        for image in images:
            if image not in self.images: count += 1
        return count <= 16**2 - len(self.images)


handler = TextureAtlasGenerator()

