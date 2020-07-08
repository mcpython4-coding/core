"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
"""
classes will be removed in the future as they can be replaced by tags
"""
import mcpython.ResourceLocator
import logger


class BlockConfigEntry:
    """
    Entry class for BlockConfig
    """

    def __init__(self, configname: str):
        """
        creates am mew entry
        :param configname: the name of the config class
        """
        self.name: str = configname
        self.affects: list = []

    def add_data(self, data: list):
        """
        adds data to the system
        :param data: an lsit of data to apply
        """
        self.affects += data

    def contains(self, item):
        """
        will check if the item is marked as affected
        :param item: the item to check
        """
        return item in self.affects

    def __contains__(self, item): return self.contains(item)


ENTRIES = dict()  # the entries
ENTRYS = ENTRIES  # todo: remove in a1.2.0


for file in mcpython.ResourceLocator.get_all_entries_special("assets/config/block"):
    if file.endswith("/"): continue
    name = file.split("/")[-1].split(".")[0]
    if name not in ENTRYS: ENTRYS[name] = BlockConfigEntry(name)
    try:
        ENTRYS[name].add_data(mcpython.ResourceLocator.read(file, mode="json"))
    except:
        logger.write_exception("[ERROR] failed to load block config file {}".format(file))

