"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import storage.datafixer.IDataFixer


@G.registry
class GeneralFix(storage.datafixer.IDataFixer.IGeneralDataFixer):
    NAME = 4

    LOAD_FIXES = []

    UPGRADES_TO = 5


@G.registry
class ChunkFixer(storage.datafixer.IDataFixer.IDataFixer):
    # NAME should be: "<version from>-<version to>:<part>"
    NAME = "4-5:minecraft:chunk"

    TRANSFORMS = (4, 5)  # from, to
    PART = "minecraft:chunk"  # which part it fixes, only one per part is executed

    @classmethod
    def fix(cls, savefile, dimension, region):
        data = savefile.access_file_pickle("dim/{}/{}_{}.region".format(dimension, *region))
        if data is None: return
        if data["version"] != 4: return
        data["version"] = 5
        for chunk in data.keys():
            if chunk == "version": continue
            cdata = data[chunk]
            if "entities" not in cdata:
                cdata["entities"] = []
        savefile.dump_file_pickle("dim/{}/{}_{}.region".format(dimension, *region), data)


@G.registry
class InventoryFixer(storage.datafixer.IDataFixer.IDataFixer):
    NAME = "4-5:minecraft:inventory_file"
    TRANSFORMS = (4, 5)  # from, to
    PART = "minecraft:inventory_file"  # which part it fixes, only one per part is executed

    @classmethod
    def fix(cls, savefile, path, file=None):
        data = savefile.access_file_pickle(file)
        data["version"] = 5
        savefile.dump_file_pickle(file, data)

