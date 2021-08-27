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
import typing

import mcpython.common.data.serializer.tags.Tag
import mcpython.common.data.serializer.tags.TagGroup
import mcpython.common.mod.ModMcpython
import mcpython.engine.ResourceLoader
from mcpython import shared
from mcpython.engine import logger


class TagHandler:
    """
    Handler for handling tags
    """

    def __init__(self):
        """
        Creates an new TagHandler instance
        """
        self.tag_groups = {}  # name -> tag group
        self.tag_locations = []
        shared.mod_loader("minecraft", "stage:tag:load", info="loading tag-groups")(
            self.load_tags
        )

    def from_data(self, tag_group: str, tag_name: str, data: dict, replace=True):
        """
        Will inject certain data
        :param tag_group: the group to use
        :param tag_name: the name of the tag
        :param data: the data to inject
        :param replace: if data should be replaced or not
        :return:
        """
        self.tag_groups.setdefault(
            tag_group, mcpython.common.data.serializer.tags.TagGroup.TagGroup(tag_group)
        ).add_from_data(tag_name, data, replace)

    def add_locations(self, locations: list):
        """
        Will add possible tag locations for later loading
        :param locations: the locations to add
        """
        self.tag_locations += locations

    def reload(self):
        """
        Will reload all tag-related data
        """
        self.tag_groups.clear()
        self.load_tags(direct_call=True)

    def load_tags(self, direct_call=False):
        """
        Will load the tags
        :param direct_call: if build now or in the loading stage for it
        """
        for row in [
            mcpython.engine.ResourceLoader.get_all_entries(x)
            for x in self.tag_locations
        ]:
            for address in row:
                if address.endswith("/"):
                    continue

                data = mcpython.engine.ResourceLoader.read_json(address)
                s = address.split("/")
                modname = s[s.index("data") + 1]
                name = "#{}:{}".format(
                    modname, "/".join(s[s.index("tags") + 2 :]).split(".")[0]
                )

                self.from_data(
                    s[s.index("tags") + 1],
                    name,
                    data,
                    data["replace"] if "replace" in data else True,
                )

        for tag_group in shared.tag_handler.tag_groups.values():
            if direct_call:
                tag_group.build()
            else:
                mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
                    "stage:tag:load",
                    tag_group.build,
                    info="loading tag-group '{}'".format(tag_group.name),
                )

    def get_tag_for(
        self, name: str, group: str, or_else_none=False
    ) -> typing.Optional[mcpython.common.data.serializer.tags.Tag.Tag]:
        """
        Will return the tag by name and group
        :param name: the name to use
        :param group: the group to use
        :param or_else_none: return None if tag not found?
        :return: the tag instance
        :raises ValueError: when the tag is not found
        """
        if group not in self.tag_groups or name not in self.tag_groups[group].tags:
            if or_else_none:
                return
            raise ValueError("unknown tag '{}' in group '{}'".format(name, group))
        return self.tag_groups[group].tags[name]

    def get_entries_for(self, name: str, group: str) -> typing.List[str]:
        """
        Will return the tag by name and group
        :param name: the name to use
        :param group: the group to use
        :return: the tag instance
        """
        if group not in self.tag_groups or name not in self.tag_groups[group].tags:
            logger.println("unknown tag '{}' in group '{}'".format(name, group))
            return []

        return self.tag_groups[group].tags[name].entries

    def get_tags_for_entry(
        self, identifier: str, group: str
    ) -> typing.List[mcpython.common.data.serializer.tags.Tag.Tag]:
        """
        Will return an list of all tag instances these instance does occur in
        :param identifier: the identifier to search for
        :param group: the group to search in
        :return: an list of Tag-instances
        """
        taglist = []
        for tag in self.tag_groups[group].tags.values():
            if identifier in tag.entries:
                taglist.append(tag)

        return taglist

    def has_entry_tag(self, identifier: str, group: str, tag_name: str) -> bool:
        """
        Check if an given tag has an entry in it
        :param identifier: the entry to check
        :param group: the group to check for
        :param tag_name: the tag name to check for
        :return: if the identifier is in the given tag
        """
        tag = self.get_tag_for(tag_name, group, or_else_none=True)
        return tag is not None and identifier in tag.entries


shared.tag_handler = TagHandler()


def add_from_location(loc: str):
    """
    Adds tags from an given scope for an given namespace where loc is the name of the namespace
    :param loc: the namespace
    WARNING: when adding outside normal build period, errors may occur
    """
    shared.tag_handler.tag_locations += [
        x.format(loc)
        for x in [
            "data/{}/tags/items",
            "data/{}/tags/naming",
            "data/{}/tags/blocks",
            "data/{}/tags/functions",
            "data/{}/tags/rendering",
        ]
    ]


@shared.mod_loader("minecraft", "stage:tag:group", info="adding tag group locations")
def load_default_tags():
    add_from_location("minecraft")
    add_from_location("forge")
