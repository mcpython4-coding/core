"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.data.tags.Tag
import mcpython.util.math


class TagGroup:
    """
    class for holding an group of tags. e.g. all items
    """

    def __init__(self, name: str):
        """
        creates an new tag group
        :param name: the name of the group
        """
        self.name = name
        self.tags = {}
        self.cache = {}

    def add_from_data(self, tagname: str, data: dict, replace=True):
        """
        will insert
        :param tagname: the tag name to set
        :param data: the data to inject
        :param replace: if the existing tag should be removed
        :return:
        """
        if replace:
            self.tags[tagname] = mcpython.common.data.tags.Tag.Tag.from_data(
                self, tagname, data
            )
        else:
            self.tags.setdefault(
                tagname, mcpython.common.data.tags.Tag.Tag(self, tagname, [])
            ).entries.extend(data["values"])

    def build(self):
        """
        will "build" the tag group
        """
        # we need to sort after dependency
        depend_list = []
        for tag in self.tags.values():
            depend_list.append((tag.name, tag.get_dependencies()))
        sort = mcpython.util.math.topological_sort(depend_list)
        for tagname in sort:
            self.tags[tagname].build()
        self.cache.clear()

    def get_tags_for(self, obj, cache=False) -> list:
        """
        will return all tags for an given object
        :param obj:
        :param cache: if data should be cached
        """
        if obj in self.cache:
            return self.cache[obj]
        result = []
        for tag_name in self.tags:
            if obj in self.tags[tag_name].entries:
                result.append(tag_name)
        if cache:
            self.cache[obj] = result
        return result

    def provides_object_tag(self, obj, tag_name: str) -> bool:
        """
        checks if the object has an given tag
        :param obj: the object to check
        :param tag_name: the tag to check for
        """
        return obj in self.tags[tag_name].entries

    def provides_object_any_tag(self, obj, taglist: list) -> bool:
        """
        return if the given object is in any of the given tag names
        :param obj: the object to check
        :param taglist: the list of tag names to check
        """
        for tag in taglist:
            if self.provides_object_tag(obj, tag):
                return True
        return False
