"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import storage.datafixer.IDataFixer


@G.registry
class GeneralFix(storage.datafixer.IDataFixer.IGeneralDataFixer):
    NAME = 1

    LOAD_FIXES = []

    UPGRADES_TO = 2


@G.registry
class ChunkFixer(storage.datafixer.IDataFixer.IDataFixer):
    # NAME should be: "<version from>-<version to>:<part>"
    NAME = "1-2:minecraft:chunk"

    TRANSFORMS = (1, 2)  # from, to
    PART = "minecraft:chunk"  # which part it fixes, only one per part is executed

    @classmethod
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


@G.registry
class InventoryFixer(storage.datafixer.IDataFixer.IDataFixer):
    NAME = "1-2:minecraft:inventory_file"
    TRANSFORMS = (1, 2)  # from, to
    PART = "minecraft:inventory_file"  # which part it fixes, only one per part is executed

    @classmethod
    def fix(cls, savefile, path, file=None):
        data = savefile.access_file_pickle(file)
        data["version"] = 2
        savefile.dump_file_pickle(file, data)

