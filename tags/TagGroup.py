"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import tags.Tag
import util.math


class TagGroup:
    def __init__(self, name: str):
        self.name = name
        self.tags = {}
        self.cache = {}

    def add_from_data(self, tagname: str, data: dict, replace=True):
        if replace:
            self.tags.setdefault(tagname, tags.Tag.Tag.from_data(self, tagname, data))
        else:
            self.tags.setdefault(tagname, tags.Tag.Tag(self, tagname, [])).entries.extend(data["values"])

    def build(self):
        depend_list = []
        for tag in self.tags.values():
            depend_list.append((tag.name, tag.get_dependencies()))
        sort = util.math.topological_sort(depend_list)
        for tagname in sort:
            self.tags[tagname].build()

    def get_tags_for(self, obj, cache=False) -> list:
        if obj in self.cache: return self.cache[obj]
        result = []
        for tag_name in self.tags:
            if obj in self.tags[tag_name].entries:
                result.append(tag_name)
        if cache: self.cache[obj] = result
        return result

    def provides_object_tag(self, obj, tag_name: str) -> bool:
        return obj in self.tags[tag_name].entries

    def provides_object_any_tag(self, obj, taglist: list) -> bool:
        for tag in taglist:
            if self.provides_object_tag(obj, tag): return True
        return False

