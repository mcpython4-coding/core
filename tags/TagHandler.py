"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import ResourceLocator
import tags.Tag
import tags.TagGroup
import globals as G
import mod.ModMcpython
import logger


class TagHandler:
    def __init__(self):
        self.taggroups = {}  # name -> taggroup
        self.taglocations = []

    def from_data(self, taggroup: str, tagname: str, data: dict, replace=True):
        self.taggroups.setdefault(taggroup, tags.TagGroup.TagGroup(taggroup)).add_from_data(tagname, data, replace)

    def add_locations(self, locations: list):
        self.taglocations += locations

    def reload(self):
        self.taggroups.clear()
        self.load_tags(direct_call=True)

    def load_tags(self, direct_call=False):
        for row in [ResourceLocator.get_all_entries(x) for x in self.taglocations]:
            for address in row:
                if address.endswith("/"): continue
                data = ResourceLocator.read(address, "json")
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
                mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:load", taggroup.build,
                                                            info="loading tag-group '{}'".format(taggroup.name))

    def get_tag_for(self, name, group):
        if group not in self.taggroups or name not in self.taggroups[group].tags:
            raise ValueError("unknown tag '{}' in group '{}'".format(name, group))
        return self.taggroups[group].tags[name]


G.taghandler = TagHandler()


def add_from_location(loc: str):
    G.taghandler.taglocations += [x.format(loc) for x in ["data/{}/tags/items", "data/{}/tags/naming",
                                                          "data/{}/tags/blocks", "data/{}/tags/functions"]]


def on_group_add():
    add_from_location("minecraft")
    add_from_location("forge")


mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:group", on_group_add, info="adding tag group locations")

mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:load", G.taghandler.load_tags, info="loading tag-groups")

