"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import json
import os
import sys
import typing
import zipfile
from abc import ABC
import itertools

import PIL.Image

import mcpython.common.config
import mcpython.util.texture
from mcpython import logger
from mcpython import shared

"""
specifications for the resource loader system

On startup / on reload, so called ResourceLocations are created for every archive / directory in resourcepack-folder

functions to access data:
    to_filename(representation: str) -> str: returns the transformed name (for example block/dirt gets 
        assets/minecraft/textures/block/dirt.png)
    exists(filename: str) -> bool: returns if an directory exists somewhere
    read(filename: str, mode=select from None for bytes, "json", "pil", "pyglet") -> object: loads the file

How mods do interact with these?
    Mod files are automatically added to these system to make it easier to add own resources
"""


class IResourceLocator(ABC):
    """
    Base class for an class holding an link to an resource source, like and directory or zip-file
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        checks if an location is valid as an source
        :param path: the path to check
        :return: if it is valid or not
        """
        raise NotImplementedError()

    def is_in_path(self, path: str) -> bool:
        """
        checks if an local file-name is in the given path
        :param path: the file path to check
        :return: if it is in the path
        """
        raise NotImplementedError()

    def read_raw(self, path: str) -> bytes:
        """
        will read an file into the system in binary mode
        :param path: the file name to use
        :return: the content of the file loaded in binary
        """
        raise NotImplementedError()

    def read_image(self, path: str) -> PIL.Image.Image:
        """
        will read an file into the system as an PIL.Image.Image
        :param path: the file name to use
        :return: the content of the file loaded as image
        """
        raise NotImplementedError()

    def read_decoding(self, path: str, encoding: str) -> str:
        """
        will read an file into the system as an string
        :param path: the file name to use
        :param encoding: the encoding to use
        :return: the content of the file loaded as string
        """
        return self.read_raw(path).decode(encoding)

    def close(self):
        """
        Called when the resource path should be closed
        """

    def get_all_entries_in_directory(
        self, directory: str, go_sub=True
    ) -> typing.Iterator[str]:
        """
        Should return all entries in an local directory
        :param directory: the directory to check
        :param go_sub: if sub directories should be iterated or not
        :return: an list of data
        """
        raise NotImplementedError()


class ResourceZipFile(IResourceLocator):
    """
    Implementation for archives
    todo: can we cache the namelist?
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        return zipfile.is_zipfile(path)

    def __init__(self, path: str):
        self.archive = zipfile.ZipFile(path)
        self.path = path
        self.namelist_cache = self.archive.namelist()

    def is_in_path(self, filename: str) -> bool:
        return filename in self.namelist_cache

    def read_raw(self, path: str) -> bytes:
        return self.archive.read(path)

    def read_image(self, path: str) -> PIL.Image.Image:
        with open(shared.tmp.name + "/resource_output.png", mode="wb") as f:
            f.write(self.archive.read(path))
        return PIL.Image.open(shared.tmp.name + "/resource_output.png")

    def close(self):
        self.archive.close()

    def get_all_entries_in_directory(
        self, directory: str, go_sub=True
    ) -> typing.Iterator[str]:
        for entry in self.namelist_cache:
            if entry.startswith(directory):
                if go_sub or (
                    directory.count("/") == entry.count("/") - 1
                    and directory.count("\\") == directory.count("\\")
                ):
                    yield entry

    def __repr__(self):
        return "ResourceZipFileOf({})".format(self.path)


class ResourceDirectory(IResourceLocator):
    """
    Implementation for raw directories
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isdir(path)

    def __init__(self, path: str):
        self.path = path.replace("\\", "/")

    def is_in_path(self, filename: str) -> bool:
        return os.path.isfile(os.path.join(self.path, filename))

    def read_raw(self, path: str) -> bytes:
        if not os.path.exists(path):
            path = self.path + ("" if path.startswith("/") else "/") + path
        with open(path, mode="rb") as f:
            data: bytes = f.read()
        return data

    def read_image(self, path: str) -> PIL.Image.Image:
        return PIL.Image.open(os.path.join(self.path, path))

    def get_all_entries_in_directory(
        self, directory: str, go_sub=True
    ) -> typing.Iterator[str]:
        if not os.path.isdir(self.path + "/" + directory):
            return []
        if not go_sub:
            return (
                (f := os.path.join(self.path, directory, e))
                + ("" if os.path.isdir(f) else "/")
                for e in os.listdir(directory)
            )
        for root, dirs, files in os.walk(self.path + "/" + directory):
            for name in files:
                file = os.path.join(root, name).replace("\\", "/")
                yield "/".join(file.split("/")[self.path.count("/") + 1 :])
            for name in dirs:
                file = os.path.join(root, name).replace("\\", "/")
                yield "/".join(file.split("/")[self.path.count("/") + 1 :]) + "/"

    def __repr__(self):
        return "ResourceDirectoryOf({})".format(self.path)


RESOURCE_PACK_LOADERS = [
    ResourceZipFile,
    ResourceDirectory,
]  # data loaders for the resource locations
RESOURCE_LOCATIONS = []  # an list of all resource locations in the system
# todo: add manager class for this


def load_resource_packs():
    """
    will load the resource packs found in the paths for it
    """
    close_all_resources()
    if not os.path.exists(shared.home + "/resourcepacks"):
        os.makedirs(shared.home + "/resourcepacks")
    for file in os.listdir(shared.home + "/resourcepacks"):
        if file in [
            "{}.jar".format(mcpython.common.config.MC_VERSION_BASE),
            "minecraft.zip",
        ]:
            continue
        file = shared.home + "/resourcepacks/" + file
        flag = True
        for source in RESOURCE_PACK_LOADERS:
            if flag and source.is_valid(file):
                RESOURCE_LOCATIONS.append(source(file))
                flag = False
        if flag:
            logger.println(
                "[ResourceLocator][WARNING] can't load path {}. No valid loader found!".format(
                    file
                )
            )
    i = 0
    while i < len(sys.argv):
        element = sys.argv[i]
        if element == "--addresourcepath":
            path = sys.argv[i + 1]
            if zipfile.is_zipfile(path):
                RESOURCE_LOCATIONS.append(ResourceZipFile(path))
            else:
                RESOURCE_LOCATIONS.append(ResourceDirectory(path))
            i += 2
        else:
            i += 1
    RESOURCE_LOCATIONS.append(
        ResourceDirectory(shared.local)
    )  # for local access, may be not needed
    RESOURCE_LOCATIONS.append(ResourceDirectory(shared.home))
    RESOURCE_LOCATIONS.append(ResourceDirectory(shared.build))
    if (
        shared.dev_environment
    ):  # only in dev-environment we need these special folders...
        print(shared.local)
        RESOURCE_LOCATIONS.append(ResourceDirectory(shared.local + "/resources/main"))
        RESOURCE_LOCATIONS.append(
            ResourceDirectory(shared.local + "/resources/generated")
        )
        RESOURCE_LOCATIONS.append(ResourceDirectory(shared.local + "/resources/source"))
    shared.event_handler.call("resources:load")


def close_all_resources():
    """
    will close all opened resource locations
    """
    for item in RESOURCE_LOCATIONS:
        item.close()
    RESOURCE_LOCATIONS.clear()
    if shared.event_handler:
        shared.event_handler.call("resources:close")


MC_IMAGE_LOCATIONS = [
    "block",
    "gui",
    "item",
    "entity",
    "model",
]  # how mc locations look like


def transform_name(file: str, raise_on_error=True) -> str:
    """
    will transform an MC-ResourceLocation string into an local path
    :param file: the thing to use
    :return: the transformed
    :param raise_on_error: will raise downer exception, otherwise return the file iself
    :raises NotImplementedError: when the data is invalid
    """
    f = file.split(":")
    if any([f[-1].startswith(x) for x in MC_IMAGE_LOCATIONS]):
        if len(f) == 1:
            f = "assets/minecraft/textures/{}/{}.png".format(
                f[0].split("/")[0], "/".join(f[0].split("/")[1:])
            )
        else:
            f = "assets/{}/textures/{}/{}.png".format(
                f[0], f[1].split("/")[0], "/".join(f[1].split("/")[1:])
            )
        return f
    if raise_on_error:
        logger.println(
            "can't find '{}' in resource system. Replacing with missing texture image...".format(
                file
            )
        )
        return "assets/missing_texture.png"
    return file


def exists(file: str, transform=True):
    """
    checks if an given file exists in the system
    :param file: the file to check
    :param transform: if it should be transformed for check
    :return: if it exists or not
    """
    if file.startswith("build/"):
        file = file.replace("build/", shared.build + "/", 1)
    if file.startswith(
        "@"
    ):  # special resource notation, can be used for accessing special ResourceLocations
        data = file.split("|")
        resource = data[0][1:]
        file = "|".join(data[1:])
        for x in RESOURCE_LOCATIONS:
            if x.path == resource:
                return x.is_in_path(file)
        return False
    for x in RESOURCE_LOCATIONS:
        if x.is_in_path(file):
            return True
    if transform:
        try:
            return exists(transform_name(file), transform=False)
        except NotImplementedError:
            pass
    return False


def read_raw(file: str):
    """
    will read the content of an file in binary mode
    :param file: the file to load
    :return: the content
    """
    if file.startswith("build/"):
        file = file.replace("build/", shared.build + "/", 1)
    if file.startswith(
        "@"
    ):  # special resource notation, can be used for accessing special ResourceLocations
        data = file.split("|")
        resource = data[0][1:]
        file = "|".join(data[1:])
        if file.startswith("build/"):
            file = file.replace("build/", shared.build + "/", 1)
        for x in RESOURCE_LOCATIONS:
            x: IResourceLocator
            if x.path == resource:
                try:
                    return x.read_raw(file)
                except:
                    logger.println("exception during loading file '{}'".format(file))
                    raise
        raise RuntimeError("can't find resource named {}".format(resource))
    if not exists(file, transform=False):
        file = transform_name(file)
    loc = RESOURCE_LOCATIONS[:]
    for x in loc:
        if x.is_in_path(file):
            try:
                return x.read_raw(file)
            except:
                logger.println("exception during loading file '{}'".format(file))
                raise
    raise ValueError("can't find resource '{}' in any path".format(file))


def read_image(file: str):
    """
    will read the content of an file in binary mode
    :param file: the file to load
    :return: the content
    """
    if file.startswith("build/"):
        file = file.replace("build/", shared.build + "/", 1)
    if file.startswith(
        "@"
    ):  # special resource notation, can be used for accessing special ResourceLocations
        data = file.split("|")
        resource = data[0][1:]
        file = "|".join(data[1:])
        if file.startswith("build/"):
            file = file.replace("build/", shared.build + "/", 1)
        for x in RESOURCE_LOCATIONS:
            x: IResourceLocator
            if x.path == resource:
                try:
                    return x.read_image(file)
                except:
                    logger.println("exception during loading file '{}'".format(file))
                    raise
        raise RuntimeError("can't find resource named {}".format(resource))
    if not exists(file, transform=False):
        file = transform_name(file)
    loc = RESOURCE_LOCATIONS[:]
    for x in loc:
        if x.is_in_path(file):
            try:
                return x.read_image(file)
            except:
                logger.println("exception during loading file '{}'".format(file))
                raise
    raise ValueError("can't find resource '{}' in any path".format(file))


def read_json(file):
    try:
        return json.loads(read_raw(file).decode("utf-8"))
    except:
        print(file)
        raise


def read_pyglet_image(file):
    return mcpython.util.texture.to_pyglet_image(read_image(file))


def get_all_entries(directory: str) -> typing.Iterator[str]:
    """
    will get all files & directories [ending with an "/"] of an given directory across all resource locations
    :param directory: the directory to use
    :return: an list of all found files
    """
    loc = RESOURCE_LOCATIONS
    loc.reverse()
    return itertools.chain.from_iterable(
        (x.get_all_entries_in_directory(directory) for x in loc)
    )


def get_all_entries_special(directory: str) -> typing.Iterator[str]:
    """
    returns all entries found with their corresponding '@[path]:file'-notation
    :param directory: the directory to search from
    :return: an list of found resources
    """
    return itertools.chain.from_iterable(
        (
            (
                "@{}|{}".format(x.path, s)
                for s in x.get_all_entries_in_directory(directory)
            )
            for x in RESOURCE_LOCATIONS
        )
    )


def add_resources_by_modname(modname, pathname=None):
    """
    loads the default data locations into the system for an given namespace
    :param modname: the name of the mod for the loading stages
    :param pathname: the namespace or None if the same as the mod name
    todo: make modular
    """
    if pathname is None:
        pathname = modname
    from mcpython.client.rendering.model.BlockState import BlockStateDefinition
    import mcpython.common.Language
    import mcpython.client.gui.crafting.CraftingManager
    import mcpython.common.data.tags.TagHandler
    import mcpython.common.data.loot.LootTable

    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:recipes",
        shared.crafting_handler.load,
        pathname,
        info="loading crafting recipes for mod {}".format(modname),
    )
    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:model:model_search",
        shared.model_handler.add_from_mod,
        pathname,
        info="searching for block models for mod {}".format(modname),
    )
    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:model:blockstate_search",
        BlockStateDefinition.from_directory,
        "assets/{}/blockstates".format(pathname),
        modname,
        info="searching for block states for mod {}".format(modname),
    )
    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:tag:group",
        lambda: mcpython.common.data.tags.TagHandler.add_from_location(pathname),
        info="adding tag groups for mod {}".format(modname),
    )
    mcpython.common.Language.from_mod_name(modname)
    shared.mod_loader.mods[modname].eventbus.subscribe(
        "stage:loottables:load",
        lambda: mcpython.common.data.loot.LootTable.handler.for_mod_name(
            modname, pathname
        ),
        info="adding loot tables for mod {}".format(modname),
    )
