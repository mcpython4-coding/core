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
import os
import typing

import mcpython.client.texture.TextureAtlas
import mcpython.engine.event.EventHandler
import mcpython.engine.ResourceLoader as ResourceLoader
import mcpython.util.texture
import PIL.Image
import pyglet
from mcpython import shared
from mcpython.engine import logger

LATEST_INFO_VERSION = 3


class ItemAtlasHandler:
    def __init__(self, folder=shared.build + "/item_atlases"):
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

    async def add_file_dynamic(self, internal_name: str, file: str):
        arrival = file in self.scheduled_item_files
        self.add_file(internal_name, file)

        if not arrival:
            image = (await ResourceLoader.read_image(file)).resize(
                (32, 32), PIL.Image.NEAREST
            )
            for i, atlas in enumerate(self.atlases):
                if atlas.is_free_for_slow([image]):
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

    async def build(self):
        self.atlases.clear()
        self.lookup_map.clear()

        added = {}

        while len(self.scheduled_item_files) > 0:
            for file in self.scheduled_item_files.copy():
                if not await ResourceLoader.exists(file):
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

                image = (await ResourceLoader.read_image(file)).resize(
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

    async def get_texture_info_or_add(self, name: str, file: str):
        """
        Save variant for adding an texture to the atlas
        Will ensure that the file is there, but must be fed with the texture file and name
        """

        if name not in self.lookup_map:
            await self.add_file_dynamic(name, file)

        index, pos = self.lookup_map[name]
        return self.grids[index][tuple(reversed(pos))]
