"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
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
import globals as G
import zipfile
import json
import PIL.Image
import os
import mcpython.util.texture
import sys
import mcpython.config
import logger
import typing


class IResourceLocation:
    """
    base class for an class holding an link to an resource system
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        checks if an location is valid as an source
        :param path: the path to check
        :return: if it is valid or not
        """
        raise NotImplementedError()

    def is_in_path(self, filename: str) -> bool:
        """
        checks if an local file-name is in the given path
        :param filename: the file name to check
        :return: if it is in the path
        """
        raise NotImplementedError()

    def read(self, filename: str, mode: str):
        """
        will read an file into the system
        :param filename: the file name to use
        :param mode: the mode to use
        :return: the content of the file loaded in the correct mode
        """
        raise NotImplementedError()

    def close(self):
        """
        implement if you need to close an resource on end
        """

    def get_all_entries_in_directory(self, directory: str) -> list:
        """
        should return all entries in an local directory
        :param directory: the directory to check
        :return: an list of data

        todo: make generator
        """
        raise NotImplementedError()


class ResourceZipFile(IResourceLocation):
    """
    implementation for archives
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        return zipfile.is_zipfile(path)

    def __init__(self, path: str):
        self.archive = zipfile.ZipFile(path)
        self.path = path

    def is_in_path(self, filename: str) -> bool:
        return filename in self.archive.namelist()

    def read(self, filename: str, mode: str):
        if mode is None:
            return self.archive.read(filename)
        elif mode == "json":
            return json.loads(self.archive.read(filename))
        elif mode == "pil":
            with open(G.tmp.name+"/resource_output.png", mode="wb") as f:
                f.write(self.archive.read(filename))
            return PIL.Image.open(G.tmp.name+"/resource_output.png")
        elif mode == "pyglet":
            return mcpython.util.texture.to_pyglet_image(self.read(filename, "pil"))
        else:
            raise ValueError("unsupported mode {}".format(mode))

    def close(self):
        self.archive.close()

    def get_all_entries_in_directory(self, directory: str, go_sub=True) -> list:
        result = []
        for entry in self.archive.namelist():
            if entry.startswith(directory):
                if go_sub or (directory.count("/") == entry.count("/") - 1 and
                              directory.count("\\") == directory.count("\\")):
                    result.append(entry)
        return result


class ResourceDirectory(IResourceLocation):
    """
    implementation for raw directories
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isdir(path)

    def __init__(self, path: str):
        self.path = path.replace("\\", "/")

    def is_in_path(self, filename: str) -> bool:
        return os.path.isfile(os.path.join(self.path, filename))

    def read(self, filename: str, mode: str):
        file = filename
        if not os.path.exists(file):
            file = self.path + ("" if filename.startswith("/") else "/") + filename
        with open(file, mode="rb") as f:
            data: bytes = f.read()
        if mode is None: return data
        if mode == "json": return json.loads(data.decode("UTF-8"))
        if mode == "pil": return PIL.Image.open(os.path.join(self.path, filename))
        if mode == "pyglet":
            return mcpython.util.texture.to_pyglet_image(self.read(filename, "pil"))

    def get_all_entries_in_directory(self, directory: str) -> list:
        if not os.path.isdir(self.path + "/" + directory): return []
        file_list = []
        for root, dirs, files in os.walk(self.path+"/"+directory):
            for name in files:
                file = os.path.join(root, name).replace("\\", "/")
                file_list.append("/".join(file.split("/")[self.path.count("/")+1:]))
            for name in dirs:
                file = os.path.join(root, name).replace("\\", "/")
                file_list.append("/".join(file.split("/")[self.path.count("/") + 1:]) + "/")
        return file_list


RESOURCE_PACK_LOADERS = [ResourceZipFile, ResourceDirectory]  # data loaders for the resource locations
RESOURCE_LOCATIONS = []  # an list of all resource locations in the system


def load_resource_packs():
    """
    will load the resource packs found in the paths for it
    """
    close_all_resources()
    if not os.path.exists(G.home+"/resourcepacks"):
        os.makedirs(G.home+"/resourcepacks")
    for file in os.listdir(G.home+"/resourcepacks"):
        if file in ["{}.jar".format(mcpython.config.MC_VERSION_BASE), "minecraft.zip"]: continue
        file = G.home+"/resourcepacks/" + file
        flag = True
        for source in RESOURCE_PACK_LOADERS:
            if flag and source.is_valid(file):
                RESOURCE_LOCATIONS.append(source(file))
                flag = False
        if flag:
            logger.println("[ResourceLocator][WARNING] can't load path {}. No valid loader found!".format(file))
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
    RESOURCE_LOCATIONS.append(ResourceDirectory(G.local))   # for local access, may be not needed
    if G.dev_environment:
        RESOURCE_LOCATIONS.append(ResourceDirectory(G.local + "/resources/generated"))
        RESOURCE_LOCATIONS.append(ResourceDirectory(G.local + "/resources/main"))
        RESOURCE_LOCATIONS.append(ResourceDirectory(G.local + "/resources/source"))
    RESOURCE_LOCATIONS.append(ResourceDirectory(G.home))
    RESOURCE_LOCATIONS.append(ResourceDirectory(G.build))
    G.eventhandler.call("resources:load")


def close_all_resources():
    """
    will close all opened resource locations
    """
    for item in RESOURCE_LOCATIONS:
        item.close()
    RESOURCE_LOCATIONS.clear()
    if G.eventhandler:
        G.eventhandler.call("resources:close")


MC_IMAGE_LOCATIONS = ["block", "gui", "item", "entity", "model"]  # how mc locations look like


def transform_name(file: str) -> str:
    """
    will transform an MC-ResourceLocation string into an local path
    :param file: the thing to use
    :return: the transformed
    :raises NotImplementedError: when the data is invalid
    """
    f = file.split(":")
    if any([f[-1].startswith(x) for x in MC_IMAGE_LOCATIONS]):
        if len(f) == 1:
            f = "assets/minecraft/textures/{}/{}.png".format(f[0].split("/")[0], "/".join(f[0].split("/")[1:]))
        else:
            f = "assets/{}/textures/{}/{}.png".format(f[0], f[1].split("/")[0], "/".join(f[1].split("/")[1:]))
        return f
    raise NotImplementedError("can't transform name '{}' to valid path".format(file))


def exists(file: str, transform=True):
    """
    checks if an given file exists in the system
    :param file: the file to check
    :param transform: if it should be transformed for check
    :return: if it exists or not
    """
    if file.startswith("@"):  # special resource notation, can be used for accessing special ResourceLocations
        data = file.split("|")
        resource = data[0][1:]
        file = "|".join(data[1:])
        for x in RESOURCE_LOCATIONS:
            if x.path == resource:
                return x.is_in_path(file)
        raise RuntimeError("can't find resource named '{}'".format(resource))
    for x in RESOURCE_LOCATIONS:
        if x.is_in_path(file):
            return True
    if transform:
        try:
            return exists(transform_name(file), transform=False)
        except NotImplementedError:
            pass
    return False


def read(file: str, mode: typing.Union[None, str] = None):
    """
    will read the content of an file
    :param file: the file to load
    :param mode: the mode to load in, or None for binary
    :return: the content
    """
    if file.startswith("@"):  # special resource notation, can be used for accessing special ResourceLocations
        data = file.split("|")
        resource = data[0][1:]
        file = "|".join(data[1:])
        for x in RESOURCE_LOCATIONS:
            if x.path == resource:
                try:
                    return x.read(file, mode)
                except json.JSONDecodeError:
                    print("json error in file {}".format(file))
                    raise
        raise RuntimeError("can't find resource named {}".format(resource))
    if not exists(file, transform=False):
        file = transform_name(file)
    if os.path.exists(G.local+"/"+file):  # special, local-only location
        if mode == "pil":
            return PIL.Image.open(G.local+"/"+file)
    loc = RESOURCE_LOCATIONS[:]
    for x in loc:
        if x.is_in_path(file):
            try:
                return x.read(file, mode)
            except:
                logger.println("exception during loading file '{}'".format(file))
                raise
    raise ValueError("can't find resource '{}' in any path".format(file))


def get_all_entries(directory: str) -> list:
    """
    will get all files & directories [ending with an "/"] of an given directory across all resource locations
    :param directory: the directory to use
    :return: an list of all found files
    todo: make return an generator
    """
    result = []
    loc = RESOURCE_LOCATIONS
    loc.reverse()
    for x in loc:
        result += x.get_all_entries_in_directory(directory)
    return list(set(result))


def get_all_entries_special(directory: str) -> list:
    """
    returns all entries found with their corresponding '@[path]:file'-notation
    :param directory: the directory to searc from
    :return: an list of found resources
    todo: make use an generator
    """
    result = []
    for x in RESOURCE_LOCATIONS:
        result += ["@{}|{}".format(x.path, s) for s in x.get_all_entries_in_directory(directory)]
    return result


def add_resources_by_modname(modname, pathname=None):
    """
    loads the default data locations into the system for an given namespace
    :param modname: the name of the mod for the loading stages
    :param pathname: the namespace or None if the same as the mod name
    """
    if pathname is None: pathname = modname
    from mcpython.rendering.model.BlockState import BlockStateDefinition
    import mcpython.Language
    import mcpython.crafting.CraftingHandler
    import mcpython.tags.TagHandler
    import mcpython.loot.LootTable
    G.modloader.mods[modname].eventbus.subscribe("stage:recipes", G.craftinghandler.load, pathname,
                                                 info="loading crafting recipes for mod {}".format(modname))
    G.modloader.mods[modname].eventbus.subscribe("stage:model:model_search", G.modelhandler.add_from_mod, pathname,
                                                 info="searching for block models for mod {}".format(modname))
    G.modloader.mods[modname].eventbus.subscribe("stage:model:blockstate_search", BlockStateDefinition.from_directory,
                                                 "assets/{}/blockstates".format(pathname), modname,
                                                 info="searching for block states for mod {}".format(modname))
    G.modloader.mods[modname].eventbus.subscribe("stage:tag:group", lambda: mcpython.tags.TagHandler.add_from_location(
        pathname), info="adding tag groups for mod {}".format(modname))
    mcpython.Language.from_mod_name(modname)
    G.modloader.mods[modname].eventbus.subscribe("stage:loottables:load", lambda: mcpython.loot.LootTable.
                                                 handler.for_mod_name(modname, pathname),
                                                 info="adding loot tables for mod {}".format(modname))

