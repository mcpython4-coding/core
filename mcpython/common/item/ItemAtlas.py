"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.texture.TextureAtlas
import mcpython.ResourceLocator
import mcpython.util.texture
from mcpython import shared as G, logger
import pickle
import os
import PIL.Image
import pyglet
import mcpython.common.event.EventHandler

LATEST_INFO_VERSION = 2


class ItemAtlasHandler:
    def __init__(self, folder=G.build + "/itematlases"):
        self.scheduled_item_files = set()
        self.atlases = []
        self.atlas_files = []
        self.atlas_grids = []
        self.allocation_table = {}
        self.file_relocate = {}
        self.prevent_resize = set()
        self.folder = folder

    def schedule_item_file(self, file: str):
        if not mcpython.ResourceLocator.exists(file):
            self.file_relocate[file] = "assets/missing_texture.png"
            self.scheduled_item_files.add("assets/missing_texture.png")
            logger.println(
                "[WARN] image at '{}' could not be allocated. Replacing with missing texture...".format(
                    file
                )
            )
            return
        self.scheduled_item_files.add(
            mcpython.ResourceLocator.transform_name(file, raise_on_error=False)
        )

    def load(self):
        if G.prebuilding:
            return
        if not os.path.isfile(self.folder + "/info.pkl"):
            return
        with open(self.folder + "/info.pkl", mode="rb") as f:
            data = pickle.load(f)
        if data["version"] != LATEST_INFO_VERSION:
            logger.println(
                "[FATAL] invalid item atlas version {} (not supported)".format(
                    data["version"]
                )
            )
            logger.println("[FATAL] skipping loading old item atlas...}")
            return
        self.allocation_table = data["allocation"]
        self.file_relocate.update(**data["relocate"])
        for i, d in enumerate(data["atlases"]):
            f = self.folder + "/atlas_{}.png".format(i)
            if not os.path.exists(f):
                continue
            atlas = mcpython.texture.TextureAtlas.TextureAtlas()
            atlas.texture = PIL.Image.open(f)
            atlas.free_space = d["free"]
            self.atlases.append(atlas)
            self.atlas_files.append(d["table"])

    def build(self):
        if len(self.atlases) == 0:
            self.atlases.append(mcpython.texture.TextureAtlas.TextureAtlas())
            self.atlas_files.append({})
        for file in self.scheduled_item_files:
            ofile = file
            if file in self.file_relocate:
                file = self.file_relocate[file]
            if file in self.allocation_table:
                continue
            if "assets/missing_texture.png" in file:
                self.allocation_table[ofile] = (0, (0, 0))
                continue
            if mcpython.ResourceLocator.exists(file):
                image = mcpython.ResourceLocator.read(file, "pil")
            else:
                self.allocation_table[ofile] = (
                    0,
                    (0, 0),
                )  # replace it by missing texture and end
                continue
            if file not in self.prevent_resize:
                image = image.resize((32, 32), PIL.Image.NEAREST)
            for i, atlas in enumerate(self.atlases):
                if len(atlas.free_space) > 0:
                    pos = atlas.add_image(image)
                    self.allocation_table[ofile] = (i, pos)
                    self.atlas_files[i][ofile] = pos
                    break
            else:
                self.atlases.append(mcpython.texture.TextureAtlas.TextureAtlas())
                self.atlas_files.append({})
                pos = self.atlases[-1].add_image(image)
                self.allocation_table[ofile] = (len(self.atlases) - 1, pos)
                self.atlas_files[-1][ofile] = pos
        for atlas in self.atlases:
            image = mcpython.util.texture.to_pyglet_image(atlas.texture)
            self.atlas_grids.append(pyglet.image.ImageGrid(image, *atlas.size))

    def dump(self):
        data = {
            "version": LATEST_INFO_VERSION,
            "atlases": [],
            "allocation": self.allocation_table,
            "relocate": self.file_relocate,
        }
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        for i, atlas in enumerate(self.atlases):
            atlas.texture.save(self.folder + "/atlas_{}.png".format(i))
            data["atlases"].append(
                {"id": i, "table": self.atlas_files[i], "free": atlas.free_space}
            )
        with open(self.folder + "/info.pkl", mode="wb") as f:
            pickle.dump(data, f)

    def get_texture_info(self, file: str):
        file = mcpython.ResourceLocator.transform_name(file, raise_on_error=False)
        if file not in self.allocation_table:
            self.schedule_item_file(file)
            # logger.println("[FATAL] tried to access '{}' (which is not arrival) for getting texture info for atlas".format(file))
            # logger.println("[FATAL] this normally indicates an missing addition to the texture atlas or an broken rendering system")
            return self.atlas_grids[0][0, 0]

        atlas_id, position = self.allocation_table[file]
        x, y = position[0], position[1]
        return self.atlas_grids[atlas_id][y, x]
