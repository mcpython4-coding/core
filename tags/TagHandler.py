"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import ResourceLocator
import tags.Tag
import tags.TagGroup
import globals as G


class TagHandler:
    def __init__(self):
        self.taggroups = {}  # name -> taggroup
        self.taglocations = ["data/minecraft/tags/items", "data/minecraft/tags/naming"]

    def load(self):
        for row in [ResourceLocator.get_all_entrys(x) for x in self.taglocations]:
            for address in row:
                if address.endswith("/"): continue
                data = ResourceLocator.read(address, "json")
                # todo: implement overwrite & extend system
                name = "#minecraft:{}".format(address.split("/")[-1].split(".")[0])
                self.from_data(address.split("/")[-2], name, data)
        for taggroup in self.taggroups.values():
            taggroup.build()
        # print(self.taggroups["items"].tags)

    def from_data(self, taggroup: str, tagname: str, data: dict):
        self.taggroups.setdefault(taggroup, tags.TagGroup.TagGroup(taggroup)).add_from_data(tagname, data)


G.taghandler = TagHandler()

