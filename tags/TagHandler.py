"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import ResourceLocator
import tags.Tag
import tags.TagGroup
import globals as G
import mod.ModMcpython


class TagHandler:
    def __init__(self):
        self.taggroups = {}  # name -> taggroup
        self.taglocations = []

    def from_data(self, taggroup: str, tagname: str, data: dict, replace=True):
        self.taggroups.setdefault(taggroup, tags.TagGroup.TagGroup(taggroup)).add_from_data(tagname, data, replace)

    def add_locations(self, locations: list):
        self.taglocations += locations


G.taghandler = TagHandler()


def on_group_add():
    G.taghandler.taglocations += ["data/minecraft/tags/items", "data/minecraft/tags/naming",
                                  "data/minecraft/tags/blocks", "data/forge/tags/items", "data/forge/tags/blocks"]


def check_tags():
    for row in [ResourceLocator.get_all_entries(x) for x in G.taghandler.taglocations]:
        for address in row:
            if address.endswith("/"): continue
            data = ResourceLocator.read(address, "json")
            s = address.split("/")
            modname = s[s.index("data")+1]
            name = "#{}:{}".format(modname, "/".join(s[s.index("tags")+2:]).split(".")[0])
            G.taghandler.from_data(s[s.index("tags")+1], name, data, data["replace"] if "replace" in data else True)
    for taggroup in G.taghandler.taggroups.values():
        mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:load", taggroup.build, info="loading taggroup {}".
                                                    format(taggroup.name))


mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:group", on_group_add, info="adding tag group names")

mod.ModMcpython.mcpython.eventbus.subscribe("stage:tag:load", check_tags, info="searching for tags in groups")

