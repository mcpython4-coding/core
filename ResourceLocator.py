"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
"""
specifications for the resource loader system

On startup / on reload, so called ResourceLocations are created for every archive / directory in resourcepack-folder

functions to access data:
    to_filename(representation: str) -> str: returns the transformed name (for example block/dirt gets 
        assets/minecraft/textures/block/dirt.png)
    exists(filename: str) -> bool: returns if an directory exists somewhere
    read(filename: str, mode=select from None for bytes, "json", "pil", "pyglet") -> object: loads the file
"""

import globals as G
import zipfile
import json
import PIL.Image
import pyglet.image
import os
import util.texture


class IResourceLocation:
    @staticmethod
    def is_valid(path: str) -> bool: raise NotImplementedError()

    def is_in_path(self, filename: str) -> bool: raise NotImplementedError()

    def read(self, filename: str, mode: str): raise NotImplementedError()

    def close(self): pass

    def get_all_entrys_in_directory(self, directory: str) -> list: raise NotImplementedError()


class ResourceZipFile(IResourceLocation):
    @staticmethod
    def is_valid(path: str) -> bool: return zipfile.is_zipfile(path)

    def __init__(self, path: str):
        self.archive = zipfile.ZipFile(path)

    def is_in_path(self, filename: str) -> bool:
        return filename in self.archive.namelist()

    def read(self, filename: str, mode: str):
        if mode is None:
            return self.archive.read(filename)
        elif mode == "json":
            return json.loads(self.archive.read(filename))
        elif mode == "pil":
            with open(G.local+"/tmp/resource_output.png", mode="wb") as f:
                f.write(self.archive.read(filename))
            return PIL.Image.open(G.local+"/tmp/resource_output.png")
        elif mode == "pyglet":
            return util.texture.to_pyglet_image(self.read(filename, "pil"))
        else:
            raise ValueError("unsupported mode {}".format(mode))

    def close(self):
        self.archive.close()

    def get_all_entrys_in_directory(self, directory: str, go_sub=False) -> list:
        result = []
        for entry in self.archive.namelist():
            if entry.startswith(directory):
                if go_sub or (directory.count("/") == entry.count("/") - 1 and
                              directory.count("\\") == directory.count("\\")):
                    result.append(entry)
        return result


class ResourceDirectory(IResourceLocation):
    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isdir(path)

    def __init__(self, path: str):
        self.path = path

    def is_in_path(self, filename: str) -> bool:
        return os.path.isfile(os.path.join(self.path, filename))

    def read(self, filename: str, mode: str):
        with open(os.path.join(self.path, filename), mode="rb") as f:
            data: bytes = f.read()
        if mode is None: return data
        if mode == "json": return json.loads(data.decode("UTF-8"))
        if mode == "pil": return PIL.Image.open(os.path.join(self.path, filename))
        if mode == "pyglet":
            return util.texture.to_pyglet_image(self.read(filename, "pil"))

    def get_all_entrys_in_directory(self, directory: str) -> list:
        if not os.path.isdir(self.path + "/" + directory): return []
        return [directory + "/" + x for x in os.listdir(self.path + "/" + directory)]


RESOURCE_LOADER = [ResourceZipFile, ResourceDirectory]
RESOURCE_LOCATIONS = []


def load_resources():
    close_all_resources()
    for file in os.listdir(G.local+"/resourcepacks"):
        if file in ["1.14.4.jar", "minecraft"]: continue
        file = G.local+"/resourcepacks/" + file
        flag = True
        for source in RESOURCE_LOADER:
            if flag and source.is_valid(file):
                RESOURCE_LOCATIONS.append(source(file))
                flag = False
        if flag:
            raise RuntimeError("can't load path {}".format(file))
    RESOURCE_LOCATIONS.append(ResourceDirectory(G.local))
    RESOURCE_LOCATIONS.append(ResourceDirectory(G.local+"/resourcepacks/minecraft"))
    RESOURCE_LOCATIONS.append(ResourceZipFile(G.local+"/resourcepacks/1.14.4.jar"))


def close_all_resources():
    for item in RESOURCE_LOCATIONS:
        item.close()
    RESOURCE_LOCATIONS.clear()


MC_IMAGE_LOCATIONS = ["block", "gui"]


def transform_name(file: str) -> str:
    if any([file.startswith(x) for x in MC_IMAGE_LOCATIONS]):
        f = "assets/minecraft/textures/{}/{}.png".format(file.split("/")[0], "/".join(file.split("/")[1:]))
        return f
    raise NotImplementedError("can't transform name {} to valid path".format(file))


def exists(file):
    return any([x.is_in_path(file) for x in RESOURCE_LOCATIONS])


def read(file, mode=None):
    if not exists(file):
        file = transform_name(file)
    for x in RESOURCE_LOCATIONS:
        if x.is_in_path(file):
            try:
                return x.read(file, mode)
            except:
                # print(file)
                raise


def get_all_entrys(directory: str) -> list:
    result = []
    for x in RESOURCE_LOCATIONS:
        result += x.get_all_entrys_in_directory(directory)
    return result

