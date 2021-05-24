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
from abc import ABC

import mcpython.common.data.tags.ITagTarget
import mcpython.common.data.tags.Tag
import mcpython.util.math
from .TagTargetHolder import TagTargetHolder


class TagGroup:
    """
    class for holding an group of tags. e.g. all items
    """

    TAG_HOLDERS: typing.Dict[str, typing.List[TagTargetHolder]] = {}

    def __init__(self, name: str):
        """
        creates an new tag group
        :param name: the name of the group
        """
        self.name = name
        self.tags = {}
        self.cache = {}

    def add_from_data(self, name: str, data: dict, replace=True):
        """
        Will insert more data into the tag system
        :param name: the tag name to set
        :param data: the data to inject
        :param replace: if the existing tag should be removed
        :return:
        """
        if replace:
            self.tags[name] = mcpython.common.data.tags.Tag.Tag.from_data(
                self, name, data
            )
        else:
            self.tags.setdefault(
                name, mcpython.common.data.tags.Tag.Tag(self, name, [])
            ).entries.extend(data["values"])

    def build(self):
        """
        Will "build" the tag group
        """
        # we need to sort after dependency
        depend_list = []
        for tag in self.tags.values():
            depend_list.append((tag.name, tag.get_dependencies()))
        sort = mcpython.util.math.topological_sort(depend_list)
        for tagname in sort:
            self.tags[tagname].build()
        self.cache.clear()
        if self.name in TagGroup.TAG_HOLDERS:
            for holder in TagGroup.TAG_HOLDERS[self.name]:
                holder.update(self)
        # print(self.name, TagGroup.TAG_HOLDERS, {name: self.tags[name].entries for name in self.tags}, sep="\n")

    def get_tags_for(self, obj: str, cache=False) -> typing.List[str]:
        """
        Will return all tags for an given object
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

    def provides_object_tag(self, obj: str, tag_name: str) -> bool:
        """
        Checks if the object has an given tag
        :param obj: the object to check
        :param tag_name: the tag to check for
        """
        return obj in self.tags[tag_name].entries

    def provides_object_tags(self, obj: str, tags: typing.List[str]) -> bool:
        """
        Returns if the given object is in all of the given tag names
        :param obj: the object to check
        :param tags: the list of tag names to check
        """
        for tag in tags:
            if not self.provides_object_tag(obj, tag):
                return False
        return True

    def provides_object_any_tag(self, obj: str, tags: typing.List[str]) -> bool:
        """
        Returns if the given object is in any of the given tag names
        :param obj: the object to check
        :param tags: the list of tag names to check
        """
        for tag in tags:
            if self.provides_object_tag(obj, tag):
                return True
        return False
