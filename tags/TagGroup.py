"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import tags.Tag
import util.math


class TagGroup:
    def __init__(self, name: str):
        self.name = name
        self.tags = {}

    def add_from_data(self, tagname: str, data: dict):
        self.tags.setdefault(tagname, tags.Tag.Tag.from_data(self, tagname, data))

    def build(self):
        depend_list = []
        for tag in self.tags.values():
            depend_list.append((tag.name, tag.get_dependencies()))
        sort = util.math.topological_sort(depend_list)
        for tagname in sort:
            self.tags[tagname].build()

