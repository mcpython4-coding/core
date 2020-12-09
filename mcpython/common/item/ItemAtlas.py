"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.client.texture.TextureAtlas
import mcpython.ResourceLoader as ResourceLoader
import mcpython.util.texture
from mcpython import shared
from mcpython import logger
import mcpython.common.event.EventHandler
import typing
import PIL.Image
import pyglet
import os

LATEST_INFO_VERSION = 3


class ItemAtlasHandler:
    def __init__(self, folder=shared.build + "/itematlases"):
        self.scheduled_item_files = {}
        self.folder = folder
        self.atlases: typing.List[
            mcpython.client.texture.TextureAtlas.TextureAtlas
        ] = []
        self.position_map = {}
        self.lookup_map = {}
        self.grids: typing.List[pyglet.image.ImageGrid] = []

    def add_file(self, internal_name: str, file: str):
        self.scheduled_item_files.setdefault(file, set()).add(internal_name)

    def add_file_dynamic(self, internal_name: str, file: str):
        arrival = file in self.scheduled_item_files
        self.add_file(internal_name, file)
        if not arrival:
            image = ResourceLoader.read_image(file).resize((32, 32), PIL.Image.NEAREST)
            for i, atlas in enumerate(self.atlases):
                if atlas.is_free_for([image]):
                    self.position_map[file] = (i, atlas.add_image(image))
                    break
            else:
                atlas = mcpython.client.texture.TextureAtlas.TextureAtlas()
                self.position_map[file] = (len(self.atlases), atlas.add_image(image))
                self.atlases.append(atlas)

                image = mcpython.util.texture.to_pyglet_image(atlas.texture)
                self.grids.append(pyglet.image.ImageGrid(image, *atlas.size))
        self.lookup_map[internal_name] = self.position_map[file]

    def load(self):
        pass

    def build(self):
        self.atlases.clear()
        self.lookup_map.clear()

        added = {}

        while len(self.scheduled_item_files) > 0:
            for file in self.scheduled_item_files.copy():
                if not ResourceLoader.exists(file):
                    if file == "assets/missing_texture.png":
                        logger.println("[FATAL] error during atlas-work")
                        del self.scheduled_item_files[file]
                        break
                    self.scheduled_item_files.setdefault(
                        "assets/missing_texture.png", []
                    ).extend(self.scheduled_item_files[file])
                    del self.scheduled_item_files[file]
                    continue

                if file == "assets/missing_texture.png":
                    self.position_map[file] = (0, (0, 0))
                    del self.scheduled_item_files[file]
                    continue

                added.setdefault(file, []).extend(self.scheduled_item_files[file])
                del self.scheduled_item_files[file]

                image = ResourceLoader.read_image(file).resize(
                    (32, 32), PIL.Image.NEAREST
                )
                for i, atlas in enumerate(self.atlases):
                    if atlas.is_free_for([image]):
                        self.position_map[file] = (i, atlas.add_image(image))
                        break
                else:
                    atlas = mcpython.client.texture.TextureAtlas.TextureAtlas()
                    self.position_map[file] = (
                        len(self.atlases),
                        atlas.add_image(image),
                    )
                    self.atlases.append(atlas)

        for file in added:
            for ref in added[file]:
                self.lookup_map[ref] = self.position_map[file]

        for atlas in self.atlases:
            image = mcpython.util.texture.to_pyglet_image(atlas.texture)
            self.grids.append(pyglet.image.ImageGrid(image, *atlas.size))

    def dump(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        for i, atlas in enumerate(self.atlases):
            atlas.texture.save(self.folder + "/atlas_{}.png".format(i))

    def get_texture_info(self, name: str):
        if name not in self.lookup_map:
            logger.print_stack(
                "[FATAL] tried to access '{}' (which is not arrival) for getting texture info for atlas".format(
                    name
                ),
                "[FATAL] this normally indicates an missing addition to the texture atlas or an broken rendering system",
            )
            return self.grids[0][0, 0]

        index, pos = self.lookup_map[name]
        return self.grids[index][tuple(reversed(pos))]

    def get_texture_info_or_add(self, name: str, file: str):
        """
        Save variant for adding an texture to the atlas
        Will ensure that the file is there, but must be fed with the texture file and name
        """

        if name not in self.lookup_map:
            self.add_file_dynamic(name, file)

        index, pos = self.lookup_map[name]
        return self.grids[index][tuple(reversed(pos))]
