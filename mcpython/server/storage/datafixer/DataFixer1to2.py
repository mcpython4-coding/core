"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
import mcpython.storage.datafixer.IDataFixer
import deprecation


@deprecation.deprecated("dev3-1", "a1.3.0")
class GeneralFix(mcpython.storage.datafixer.IDataFixer.IGeneralDataFixer):
    NAME = 1
    LOAD_FIXES = []
    UPGRADES_TO = 2


@deprecation.deprecated("dev3-1", "a1.3.0")
class ChunkFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    NAME = "1-2:minecraft:chunk"
    TRANSFORMS = (1, 2)
    PART = "minecraft:chunk"

    @classmethod
    @deprecation.deprecated("dev3-1", "a1.3.0")
    def fix(cls, savefile, dimension, region):
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: return
        if data["version"] != 1: return
        data["version"] = 2
        for chunk in data.keys():
            if chunk == "version": continue
            cdata = data[chunk]
            if "temperature" in cdata:
                del cdata["temperature"]
            if "landmass" in cdata["maps"]:
                landmass_map = cdata["maps"]["landmass"]
                del cdata["maps"]["landmass"]
                cdata["maps"]["landmass_map"] = []
                cdata["maps"]["landmass_palette"] = []
                for i in range(len(landmass_map)):
                    mass = landmass_map[i]
                    if mass not in cdata["maps"]["landmass_palette"]:
                        index = len(cdata["maps"]["landmass_palette"])
                        cdata["maps"]["landmass_palette"].append(mass)
                    else:
                        index = cdata["maps"]["landmass_palette"].index(mass)
                    cdata["maps"]["landmass_map"].append(index)
        savefile.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)


@deprecation.deprecated("dev3-1", "a1.3.0")
class InventoryFixer(mcpython.storage.datafixer.IDataFixer.IDataFixer):
    NAME = "1-2:minecraft:inventory_file"
    TRANSFORMS = (1, 2)  # from, to
    PART = "minecraft:inventory_file"  # which part it fixes, only one per part is executed

    @classmethod
    @deprecation.deprecated("dev3-1", "a1.3.0")
    def fix(cls, savefile, path, file=None):
        data = savefile.access_file_pickle(file)
        data["version"] = 2
        savefile.dump_file_pickle(file, data)

