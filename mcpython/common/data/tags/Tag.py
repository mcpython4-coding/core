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
from mcpython import logger, shared


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
        for entry in self.entries[:]:
            if isinstance(entry, str) and entry.startswith("#") and entry in self.master.tags:
                dep.append(entry)
            else:
                # todo: implement
                self.entries.remove(entry)
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
                    shared.mod_loader["minecraft"].eventbus.subscribe(
                        "stage:tag:load", self.build
                    )
                    self.load_tries += 1
                    return
                self.entries += self.master.tags[entry].entries
            elif entry not in self.entries:
                self.entries.append(entry)
