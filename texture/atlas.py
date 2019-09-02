"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import pyglet
import PIL.Image
import texture.helpers
import os
import ResourceLocator


class TextureAtlasEntry:
    def __init__(self, image):
        self.image = image
        self.generator = None
        self.atlas = None
        self.position = None

    def get_texture_atlas_and_index(self) -> tuple:
        return self.atlas, self.position

    def __eq__(self, other):
        if type(other) != TextureAtlasEntry:
            return type(other) != PIL.Image.Image and other != self.image


class TextureAtlasGenerator:
    def __init__(self):
        self.atlases = []
        self.texture_groups = []
        self.entrys = []
        self.__builed = False

    def is_builded(self):
        return self.__builed

    builded = property(fget=is_builded)

    def add_files_or_images(self, files_or_images: list):
        if self.__builed:
            raise RuntimeError("can't add to an builded texture atlas")
        if len(files_or_images) == 0: return
        images = []
        for file_or_image in files_or_images:
            if type(file_or_image) == str:
                file_or_image = ResourceLocator.ResourceLocator(file_or_image).data
            images.append(TextureAtlasEntry(file_or_image))
            images[-1].generator = self
            images[-1].image = images[-1].image.resize((64, 64))
        self.entrys.append(images)
        return images

    def build(self):
        missingtexture = PIL.Image.open(G.local+"/assets/missingtexture.png").resize((64, 64))
        self.__builed = True
        self.entrys.sort(key=lambda x: len(x))
        # print(self.entrys)
        textures = [[PIL.Image.new("RGBA", (1024, 1024)), [], (1, 0)]]  # texture, images, next_space
        textures[-1][0].paste(missingtexture, (0, 960))
        image_space = 255
        not_used = self.entrys[:]
        while len(not_used) > 0:
            print("\r", end="")
            print(len(self.entrys)-len(not_used)+1, "/", len(self.entrys), end="")
            images = not_used.pop(0)
            result = self._is_free_space(images, textures, image_space)
            if result is None:
                textures.append([PIL.Image.new("RGBA", (1024, 1024)), [], (1, 0)])
                textures[-1][0].paste(missingtexture, (0, 960))
                result = -1
            atlas = textures[result]
            for image in images:
                if not generator.image_in_array(image, atlas[1]):
                    x, y = atlas[2]
                    atlas[0].paste(image.image, (x*64, 1024-(y+1)*64))
                    image.atlas = result
                    image.position = (x, y)
                    x += 1
                    if x == 16:
                        x = 0
                        y += 1
                    atlas[2] = (x, y)
                    if image not in atlas[1]: atlas[1].append(image)
                    textures[result] = atlas
                else:
                    h_image = atlas[1][self.image_index_in_array(image, atlas[1])]
                    image.atlas = result
                    image.position = h_image.position

        self.atlases = [x[0] for x in textures]
        for i, image in enumerate(self.atlases):
            image.save(G.local+"/tmp/image_atlas_{}.png".format(i))
            self.texture_groups.append(pyglet.graphics.TextureGroup(
                pyglet.image.load(G.local+"/tmp/image_atlas_{}.png".format(i)).get_texture()))
        # do an cleanup over every entry in the atlas storing the image to add
        for entry in self.entrys:
            for e in entry:
                del e.image
        print()

    @staticmethod
    def _is_free_space(images, atlases, image_space) -> int or None:
        for i, (atlas, atlasimages, _) in enumerate(atlases):
            equal = sum([0 if not generator.image_in_array(image, atlasimages) else 1 for image in images])
            if len(atlasimages) - equal + len(images) <= image_space:
                return i

    @staticmethod
    def image_in_array(image, array) -> bool:
        array = [i if type(i) != TextureAtlasEntry else i.image for i in array]
        if type(image) == TextureAtlasEntry:
            image = image.image
        return image in array

    @staticmethod
    def image_index_in_array(image, array) -> int or None:
        array = [i if type(i) != TextureAtlasEntry else i.image for i in array]
        if type(image) == TextureAtlasEntry:
            image = image.image
        return array.index(image) if image in array else None


generator = TextureAtlasGenerator()

