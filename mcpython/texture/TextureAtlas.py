"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import PIL.Image
import mcpython.ResourceLocator
import globals as G
import pyglet
import os
import mcpython.mod.ModMcpython
import mcpython.config

MISSING_TEXTURE = mcpython.ResourceLocator.read("assets/missingtexture.png", "pil").resize((16, 16), PIL.Image.NEAREST)


class TextureAtlasGenerator:
    """
    generator system for an item atlas
    """

    def __init__(self):
        self.atlases = {}

    def add_image(self, image: PIL.Image.Image, modname: str) -> tuple:
        if modname not in self.atlases: self.atlases[modname] = [TextureAtlas()]
        image = image.crop((0, 0, image.size[0], image.size[0]))
        for atlas in self.atlases:
            if atlas.image_size == image.size:
                return atlas.add_image(image), atlas
        self.atlases[modname].append(TextureAtlas())
        return self.atlases[modname][-1].add_image(image), self.atlases[-1]

    def add_image_file(self, file: str, modname: str) -> tuple:
        return self.add_image(mcpython.ResourceLocator.read(file, "pil"), modname)

    def add_images(self, images: list, modname, one_atlased=True) -> list:
        if len(images) == 0: return []
        if not one_atlased:
            return [self.add_image(x, modname) for x in images]
        if modname not in self.atlases: self.atlases[modname] = [TextureAtlas()]
        images = [image.crop((0, 0, image.size[0], image.size[0])) for image in images]
        m_size = max(images, key=lambda a: a.size[0] * a.size[1]).size
        for atlas in self.atlases[modname]:
            if atlas.image_size == m_size:
                return [(atlas.add_image(image), atlas) for image in images]
        atlas = TextureAtlas()
        self.atlases[modname].append(atlas)
        return [(atlas.add_image(image), atlas) for image in images]

    def add_image_files(self, files: list, modname: str, one_atlased=True) -> list:
        return self.add_images([mcpython.ResourceLocator.read(x, "pil") for x in files], modname,
                               one_atlased=one_atlased)

    def output(self):
        # todo: add per-mod, at end of every processing of models
        G.eventhandler.call("textures:atlas:build:pre")
        os.makedirs(G.tmp.name + "/textureatlases")
        for modname in self.atlases:
            for i, atlas in enumerate(self.atlases[modname]):
                location = G.tmp.name + "/textureatlases/atlas_{}_{}_{}x{}.png".format(modname, i, *atlas.image_size)
                atlas.texture.save(location)
                atlas.group = pyglet.graphics.TextureGroup(pyglet.image.load(location).get_texture())
        G.eventhandler.call("textures:atlas:build:post")


class TextureAtlas:
    def __init__(self, size=(16, 16), image_size=(16, 16), add_missing_texture=True, pyglet_special_pos=True):
        self.size = size
        self.image_size = image_size
        self.pyglet_special_pos = pyglet_special_pos
        self.texture = PIL.Image.new("RGBA", (size[0] * image_size[0], size[1] * image_size[1]))
        self.free_space = set()
        for x in range(self.size[0]): self.free_space.update(set([(x, y) for y in range(self.size[1])]))
        self.images = []
        self.imagelocations = []  # an images[-parallel (x, y)-list
        if add_missing_texture: self.add_image(MISSING_TEXTURE, position=(0, 0))
        self.group = None

    def add_image(self, image: PIL.Image.Image, ind=None, position=None) -> tuple:
        if ind is None: ind = image
        if ind in self.images: return self.imagelocations[self.images.index(ind)]
        if image.size[0] > self.image_size[0] or image.size[1] > self.image_size[1]:
            self.image_size = image.size[0], image.size[0]
            self.texture = self.texture.resize(tuple(
                [self.size[i] * self.image_size[i] for i in range(2)]), PIL.Image.NEAREST)
        else:
            image = image.resize(self.image_size, PIL.Image.NEAREST)
        if len(self.free_space) == 0:
            old = self.texture
            sx, sy = self.size
            self.size = sx * 2, sy * 2
            self.texture = PIL.Image.new("RGBA", (sx * self.image_size[0] * 2, sy * self.image_size[1] * 2))
            self.texture.paste(old, (0, sy * self.image_size[0]))
            for x in range(sx * 2):
                for y in range(sy * 2):
                    if x >= sx or y >= sy:
                        self.free_space.add((x, y))
        self.images.append(ind)
        if position is None or position not in self.free_space:
            x, y = self.free_space.pop()
        else:
            x, y = position
            self.free_space.remove(position)
        self.texture.paste(image, (x * self.image_size[0], (self.size[1] - y - 1 if self.pyglet_special_pos else y) *
                                   self.image_size[1]))
        pos = x, y
        x += 1
        if x >= self.size[0]: x = 0; y += 1
        self.imagelocations.append(pos)
        return pos

    def is_free_for(self, images: list) -> bool:
        count = 0
        for image in images:
            if image not in self.images: count += 1
        return count <= self.size[0] * self.size[1] - len(self.images) or count <= len(self.free_space)


handler = TextureAtlasGenerator()

mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:textureatlas:bake", handler.output,
                                                     info="building texture atlases...")
