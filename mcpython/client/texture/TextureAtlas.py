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
import itertools
import os
import typing

import mcpython.common.config
import mcpython.engine.ResourceLoader
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.util.annotation import onlyInClient

MISSING_TEXTURE = mcpython.engine.ResourceLoader.read_image(
    "assets/missing_texture.png"
).resize((16, 16), PIL.Image.NEAREST)


@onlyInClient()
class TextureAtlasGenerator:
    """
    Generator system for a multiple underlying ItemAtlas'

    Based on some identifier
    """

    def __init__(self):
        self.atlases: typing.Dict[typing.Hashable, typing.List[TextureAtlas]] = {}

    def add_image(self, image: PIL.Image.Image, identifier: typing.Hashable) -> typing.Tuple[typing.Tuple[int, int], "TextureAtlas"]:
        """
        Adds a single pillow image to the underlying atlas system
        """
        image = image.crop((0, 0, image.size[0], image.size[0]))

        for atlas in self.atlases.setdefault(identifier, []):
            if atlas.image_size == image.size:
                return atlas.add_image(image), atlas

        self.atlases[identifier].append(TextureAtlas())
        return self.atlases[identifier][-1].add_image(image), self.atlases[identifier][-1]

    def add_image_file(self, file: str, identifier: str) -> typing.Tuple[typing.Tuple[int, int], "TextureAtlas"]:
        """
        Adds a single image by file name (loadable by resource system!)
        """
        return self.add_image(mcpython.engine.ResourceLoader.read_image(file), identifier)

    def add_images(self, images: typing.List[PIL.Image.Image], identifier: str, single_atlas=True) -> typing.List[typing.Tuple[typing.Tuple[int, int], "TextureAtlas"]]:
        if len(images) == 0:
            return []

        if not single_atlas:
            return [self.add_image(x, identifier) for x in images]

        images = [image.crop((0, 0, image.size[0], image.size[0])) for image in images]
        m_size = max(images, key=lambda a: a.size[0] * a.size[1]).size

        for atlas in self.atlases.setdefault(identifier, []):
            if atlas.image_size == m_size:
                return [(atlas.add_image(image), atlas) for image in images]

        atlas = TextureAtlas()
        self.atlases[identifier].append(atlas)
        return [(atlas.add_image(image), atlas) for image in images]

    def add_image_files(self, files: list, identifier: str, single_atlas=True) -> typing.List[typing.Tuple[typing.Tuple[int, int], "TextureAtlas"]]:
        return self.add_images([mcpython.engine.ResourceLoader.read_image(x) for x in files], identifier,
                               single_atlas=single_atlas)

    def output(self):
        # todo: add per-mod, at end of every processing of models

        shared.event_handler.call("textures:atlas:build:pre")
        os.makedirs(shared.tmp.name + "/texture_atlases", exist_ok=True)

        for identifier in self.atlases:
            for i, atlas in enumerate(self.atlases[identifier]):
                location = (
                    shared.tmp.name
                    + "/texture_atlases/atlas_{}_{}_{}x{}.png".format(
                        identifier, i, *atlas.image_size
                    )
                )
                atlas.texture.save(location)
                atlas.group = pyglet.graphics.TextureGroup(
                    pyglet.image.load(location).get_texture()
                )

        shared.event_handler.call("textures:atlas:build:post")


@onlyInClient()
class TextureAtlas:
    """
    One-texture atlas

    Contains a single underlying texture, dynamically resized when needed
    """

    def __init__(
        self,
        size=(16, 16),
        image_size=(16, 16),
        add_missing_texture=True,
        pyglet_special_pos=True,
    ):
        self.size = size
        self.image_size = image_size
        self.pyglet_special_pos = pyglet_special_pos

        # The underlying texture
        self.texture = PIL.Image.new(
            "RGBA", (size[0] * image_size[0], size[1] * image_size[1])
        )

        # Where is space for images?
        self.free_space = set(itertools.product(range(size[0]), range(size[1])))

        self.images: typing.List[PIL.Image.Image] = []
        self.image_locations: typing.List[typing.Tuple[int, int]] = []

        if add_missing_texture:
            self.add_image(MISSING_TEXTURE, position=(0, 0))

        # The pyglet texture group, only for storage reasons
        self.group: typing.Optional[pyglet.graphics.TextureGroup] = None

    def add_image(self, image: PIL.Image.Image, position=None) -> typing.Tuple[int, int]:
        """
        Adds an image to the atlas and returns the position of it in the atlas
        """

        if image in self.images:
            return self.image_locations[self.images.index(image)]

        if image.size[0] > self.image_size[0] or image.size[1] > self.image_size[1]:
            self.image_size = image.size[0], image.size[0]
            self.texture = self.texture.resize(
                tuple([self.size[i] * self.image_size[i] for i in range(2)]),
                PIL.Image.NEAREST,
            )
        else:
            image = image.resize(self.image_size, PIL.Image.NEAREST)

        if len(self.free_space) == 0:
            # todo: export to separate function
            old = self.texture
            sx, sy = self.size
            self.size = sx * 2, sy * 2
            self.texture = PIL.Image.new(
                "RGBA", (sx * self.image_size[0] * 2, sy * self.image_size[1] * 2)
            )
            self.texture.paste(old, (0, sy * self.image_size[0]))
            for x in range(sx * 2):
                for y in range(sy * 2):
                    if x >= sx or y >= sy:
                        self.free_space.add((x, y))

        self.images.append(image)

        if position is None or position not in self.free_space:
            x, y = pos = self.free_space.pop()
        else:
            x, y = pos = position
            self.free_space.remove(position)

        self.texture.paste(
            image,
            (
                x * self.image_size[0],
                (self.size[1] - y - 1 if self.pyglet_special_pos else y)
                * self.image_size[1],
            ),
        )

        self.image_locations.append(pos)

        return pos

    def is_free_for(self, images: list) -> bool:
        # todo: is there a better way to check for images present (duplicated images are skipped)?
        return len(images) <= len(self.free_space)

    def is_free_for_slow(self, images: list) -> bool:
        count = 0
        for image in images:
            if image not in self.images:
                count += 1
        
        return count <= self.size[0] * self.size[1] - len(self.images) or count <= len(
            self.free_space
        )


handler = TextureAtlasGenerator()

shared.mod_loader("minecraft", "stage:textureatlas:on_bake")(handler.output)
