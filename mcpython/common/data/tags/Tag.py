"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G, logger
import mcpython.common.mod.ModMcpython


class Tag:
    """
    class holding an single tag
    """

    @staticmethod
    def from_data(master, tagname: str, data: dict):
        """
        will create an new tag from data
        :param master: the group to use
        :param tagname: the name of the tag
        :param data: the data to use
        :return the tag instance
        """
        return Tag(master, tagname, data["values"])

    def __init__(self, master, name: str, entries: list):
        """
        will create an new tag instance from an list of entries
        :param master: the tag group to use
        :param name: the name of the tag
        :param entries: the entries to use
        """
        self.entries = entries
        self.master = master
        self.name = name
        self.load_tries = 0

    def get_dependencies(self) -> list:
        """
        will return an list of tags these tag links to
        :return the list
        """
        dep = []
        for entry in self.entries:
            if entry.startswith("#") and entry in self.master.tags:
                dep.append(entry)
        return dep

    def build(self):
        """
        will build the tag
        """
        raw = self.entries.copy()
        old_entries = self.entries.copy()
        self.entries.clear()
        for entry in raw:
            if entry.startswith("#"):
                if entry not in self.master.tags:
                    if self.load_tries > 4:
                        logger.println(
                            "[TAG][FATAL] failed to load tag {} as tag {} was not found".format(
                                self.name, entry
                            )
                        )
                        self.load_tries = 0
                        old_entries.remove(entry)
                        continue
                    self.entries = old_entries
                    mcpython.mod.ModMcpython.mcpython.eventbus.subscribe(
                        "stage:tag:load", self.build
                    )
                    self.load_tries += 1
                    return
                self.entries += self.master.tags[entry].entries
            else:
                self.entries.append(entry)
