"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared as G
import mcpython.ResourceLoader
import mcpython.common.mod.ModMcpython
import mcpython.common.data.tags.Tag
import mcpython.common.data.tags.TagGroup


class TagHandler:
    """
    handler for handling tags
    """

    def __init__(self):
        """
        creates an new TagHandler instance
        """
        self.taggroups = {}  # name -> taggroup
        self.taglocations = []
        G.mod_loader("minecraft", "stage:tag:load", "loading tag-groups")(self.load_tags)

    def from_data(self, taggroup: str, tagname: str, data: dict, replace=True):
        """
        will inject certain data
        :param taggroup: the group to use
        :param tagname: the name of the tag
        :param data: the data to inject
        :param replace: if data should be replaced or not
        :return:
        """
        self.taggroups.setdefault(
            taggroup, mcpython.common.data.tags.TagGroup.TagGroup(taggroup)
        ).add_from_data(tagname, data, replace)

    def add_locations(self, locations: list):
        """
        will add possible tag locations for later loading
        :param locations: the locations to add
        """
        self.taglocations += locations

    def reload(self):
        """
        will reload all tag-related data
        """
        self.taggroups.clear()
        self.load_tags(direct_call=True)

    def load_tags(self, direct_call=False):
        """
        will load the tags
        :param direct_call: if build now or in the loading stage for it
        """
        for row in [
            mcpython.ResourceLoader.get_all_entries(x) for x in self.taglocations
        ]:
            for address in row:
                if address.endswith("/"):
                    continue
                data = mcpython.ResourceLoader.read_json(address)
                s = address.split("/")
                modname = s[s.index("data") + 1]
                name = "#{}:{}".format(
                    modname, "/".join(s[s.index("tags") + 2 :]).split(".")[0]
                )
                G.tag_handler.from_data(
                    s[s.index("tags") + 1],
                    name,
                    data,
                    data["replace"] if "replace" in data else True,
                )
        for taggroup in G.tag_handler.taggroups.values():
            if direct_call:
                # logger.println("loading tag-group {}".format(taggroup.name))
                taggroup.build()
            else:
                mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
                    "stage:tag:load",
                    taggroup.build,
                    info="loading tag-group '{}'".format(taggroup.name),
                )

    def get_tag_for(self, name: str, group: str) -> mcpython.common.data.tags.Tag.Tag:
        """
        will return the tag by name and group
        :param name: the name to use
        :param group: the group to use
        :return: the tag instance
        :raises ValueError: when the tag is not found
        """
        if group not in self.taggroups or name not in self.taggroups[group].tags:
            raise ValueError("unknown tag '{}' in group '{}'".format(name, group))
        return self.taggroups[group].tags[name]

    def get_tags_for_entry(self, identifier: str, group: str) -> list:
        """
        will return an list of all tag instances these instance does occure in
        :param identifier: the identifier to search for
        :param group: the group to search in
        :return: an list of Tag-instances
        """
        taglist = []
        for tag in self.taggroups[group].tags.values():
            if identifier in tag.entries:
                taglist.append(tag)
        return taglist

    def has_entry_tag(self, identifier: str, group: str, tag_name: str) -> bool:
        """
        check if an given tag has an entry in it
        :param identifier: the entry to check
        :param group: the group to check for
        :param tag_name: the tag name to check for
        :return: if the identifier is in the given tag
        """
        return identifier in self.get_tag_for(tag_name, group).entries


G.tag_handler = TagHandler()


def add_from_location(loc: str):
    """
    adds tags from an given scope for an given namespace where loc is the name of the namespace
    :param loc: the namespace
    WARNING: when adding outside normal build period, errors may occur
    """
    G.tag_handler.taglocations += [
        x.format(loc)
        for x in [
            "data/{}/tags/items",
            "data/{}/tags/naming",
            "data/{}/tags/blocks",
            "data/{}/tags/functions",
            "data/{}/tags/rendering",
        ]
    ]


@G.mod_loader("minecraft", "stage:tag:group", "adding tag group locations")
def on_group_add():
    add_from_location("minecraft")
    add_from_location("forge")
