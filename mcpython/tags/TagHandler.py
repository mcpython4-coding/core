"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.ResourceLocator
import mcpython.tags.Tag
import mcpython.tags.TagGroup
import globals as G
import mcpython.mod.ModMcpython
import logger


class TagHandler:
    def __init__(self):
        self.taggroups = {}  # name -> taggroup
        self.taglocations = []
        G.modloader("minecraft", "stage:tag:load", "loading tag-groups")(self.load_tags)

    def from_data(self, taggroup: str, tagname: str, data: dict, replace=True):
        self.taggroups.setdefault(taggroup, mcpython.tags.TagGroup.TagGroup(taggroup)).add_from_data(tagname, data, replace)

    def add_locations(self, locations: list):
        self.taglocations += locations

    def reload(self):
        self.taggroups.clear()
        self.load_tags(direct_call=True)

    def load_tags(self, direct_call=False):
        for row in [mcpython.ResourceLocator.get_all_entries(x) for x in self.taglocations]:
            for address in row:
                if address.endswith("/"): continue
                data = mcpython.ResourceLocator.read(address, "json")
                s = address.split("/")
                modname = s[s.index("data") + 1]
                name = "#{}:{}".format(modname, "/".join(s[s.index("tags") + 2:]).split(".")[0])
                G.taghandler.from_data(s[s.index("tags") + 1], name, data,
                                       data["replace"] if "replace" in data else True)
        for taggroup in G.taghandler.taggroups.values():
            if direct_call:
                logger.println("loading tag-group {}".format(taggroup.name))
                taggroup.build()
            else:
                mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:load", taggroup.build,
                                                            info="loading tag-group '{}'".format(taggroup.name))

    def get_tag_for(self, name: str, group: str) -> mcpython.tags.Tag.Tag:
        if group not in self.taggroups or name not in self.taggroups[group].tags:
            raise ValueError("unknown tag '{}' in group '{}'".format(name, group))
        return self.taggroups[group].tags[name]

    def get_tags_for_entry(self, identifier: str, group: str) -> list:
        taglist = []
        for tag in self.taggroups[group].tags.values():
            if identifier in tag.entries:
                taglist.append(tag)
        return taglist

    def has_entry_tag(self, identifier: str, group: str, tagname: str) -> bool:
        return identifier in self.get_tag_for(tagname, group).entries


G.taghandler = TagHandler()


def add_from_location(loc: str):
    """
    adds tags from an given scope for an given namespace where loc is the name of the namespace
    :param loc: the namespace
    WARNING: when adding outside normal build period, errors may occur
    """
    G.taghandler.taglocations += [x.format(loc) for x in ["data/{}/tags/items", "data/{}/tags/naming",
                                                          "data/{}/tags/blocks", "data/{}/tags/functions"]]


@G.modloader("minecraft", "stage:tag:group", "adding tag group locations")
def on_group_add():
    add_from_location("minecraft")
    add_from_location("forge")

