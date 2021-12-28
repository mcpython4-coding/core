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
import io

import aiofiles
import asyncio
from aiofiles import os as aio_os, ospath as async_path
import itertools
import json
import os
import sys
import typing
import zipfile
from abc import ABC

# servers don't need textures, so pillow is not required
# WARNING: this  M A Y  break other stuff
try:
    import PIL.Image as PIL_Image
except ImportError:

    if not typing.TYPE_CHECKING:
        class PIL_Image:
            class Image:
                pass

            @classmethod
            def open(cls, file: str | io.BytesIO):
                raise IOError()
    else:
        import PIL.Image as PIL_Image


import mcpython.common.config
import mcpython.util.texture
from mcpython import shared
from mcpython.engine import logger

"""
---------------------------------------------
Specifications for the resource loader system
---------------------------------------------

On startup / on reload, so called ResourceLocation's are created for every archive / directory in resourcepack-folder
and other asset sources (mod files)

functions to access data:
    to_filename(representation: str) -> str: returns the transformed name (for example block/dirt gets 
        assets/minecraft/textures/block/dirt.png)
    exists(filename: str) -> bool: returns if an directory exists somewhere
    read_<xy>(filename: str) -> object: loads the file in the speicified mode

How mods do interact with these?
    Mod files are automatically added to these system to make it easier to add own resources

There is a special class for simulating files in-memory 
"""


class IResourceLoader(ABC):
    """
    Base class for a class holding a link to a resource source, like and directory or zip-file
    (but in theory can be anything, even over network)
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        """
        Checks if a location is valid as a source to load via the constructor
        :param path: the path to check
        :return: if it is valid or not
        """
        raise NotImplementedError()

    def get_path_info(self) -> str:
        """
        Returns a unique identifier for this loader, like a path loaded from, or some mod name
        """
        raise NotImplementedError()

    async def is_in_path(self, path: str) -> bool:
        """
        Checks if a local file-name is in the given path, so it can be loaded
        :param path: the file path to check
        :return: if it is in the path
        """
        raise NotImplementedError()

    async def read_raw(self, path: str) -> bytes:
        """
        Will read a file in binary mode
        :param path: the file name to use
        :return: the content of the file loaded in binary
        """
        raise NotImplementedError()

    async def read_image(self, path: str) -> PIL_Image.Image:
        """
        Will read a file as a PIL.Image.Image
        :param path: the file name to use
        :return: the content of the file loaded as image
        """
        data = await self.read_raw(path)
        return PIL_Image.open(io.BytesIO(data))

    async def read_decoding(self, path: str, encoding: str = "utf-8") -> str:
        """
        Will read a file into the system as a string, decoding the raw bytes in the given encoding
        :param path: the file name to use
        :param encoding: the encoding to use
        :return: the content of the file loaded as string
        """
        return (await self.read_raw(path)).decode(encoding)

    def close(self):
        """
        Called when the resource path should be closed
        Should be used for cleanup
        """

    def get_all_entries_in_directory(
        self, directory: str, go_sub=True
    ) -> typing.Iterator[str]:
        """
        Should return all entries in a local directory
        :param directory: the directory to check
        :param go_sub: if sub directories should be iterated or not
        :return: a list of data
        todo: add a regex variant
        """
        raise NotImplementedError()


class ResourceZipFile(IResourceLoader):
    """
    Implementation for zip-archives
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        return zipfile.is_zipfile(path)

    def __init__(self, path: str, close_when_scheduled=True):
        self.archive = zipfile.ZipFile(path)
        self.path = path
        self.namelist_cache = self.archive.namelist()
        self.close_when_scheduled = close_when_scheduled

    def get_path_info(self) -> str:
        return self.path

    async def is_in_path(self, filename: str) -> bool:
        return filename in self.namelist_cache

    async def read_raw(self, path: str) -> bytes:
        return self.archive.read(path)

    async def read_image(self, path: str) -> PIL_Image.Image:
        data = self.archive.read(path)
        return PIL_Image.open(io.BytesIO(data))

    def close(self):
        if self.close_when_scheduled:
            self.archive.close()

    def get_all_entries_in_directory(
        self, directory: str, go_sub=True
    ) -> typing.Iterator[str]:
        for entry in self.namelist_cache:
            if entry.startswith(directory):
                if go_sub or (
                    (  # if it is an dir, same level, else one level lower
                        directory.count("/") == entry.count("/")
                        if entry.endswith("/")
                        else directory.count("/") == entry.count("/") - 1
                    )
                    and directory.count("\\") == directory.count("\\")
                ):
                    yield entry

    def __repr__(self):
        return "ResourceZipFileOf({})".format(self.path)


class ResourceDirectory(IResourceLoader):
    """
    Implementation for raw directories
    """

    @staticmethod
    def is_valid(path: str) -> bool:
        return os.path.isdir(path)

    def __init__(self, path: str):
        self.path = path.replace("\\", "/")

    def get_path_info(self) -> str:
        return self.path

    async def is_in_path(self, filename: str) -> bool:
        return await async_path.isfile(os.path.join(self.path, filename))

    async def read_raw(self, path: str) -> bytes:
        if not os.path.exists(path):
            path = self.path + ("" if path.startswith("/") else "/") + path
        async with aiofiles.open(path, mode="rb") as f:
            data: bytes = await f.read()
        return data

    async def read_image(self, path: str) -> PIL_Image.Image:
        return PIL_Image.open(os.path.join(self.path, path))

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

        # iterator os.walk is the best we have in this case
        for root, dirs, files in os.walk(self.path + "/" + directory):
            for name in files:
                file = os.path.join(root, name).replace("\\", "/")
                yield "/".join(file.split("/")[self.path.count("/") + 1 :])

            for name in dirs:
                file = os.path.join(root, name).replace("\\", "/")
                yield "/".join(file.split("/")[self.path.count("/") + 1 :]) + "/"

    def __repr__(self):
        return "ResourceDirectory({})".format(self.path)


class SimulatedResourceLoader(IResourceLoader):
    """
    In-memory resource loader instance
    """

    SIMULATOR_ID = 0

    def __init__(self):
        self.raw = {}
        self.images = {}
        self.id = SimulatedResourceLoader.SIMULATOR_ID
        SimulatedResourceLoader.SIMULATOR_ID += 1

    def debug_dump(self, directory: str):
        for file, data in self.raw.items():
            file = os.path.join(directory, file)
            d = os.path.dirname(file)
            os.makedirs(d, exist_ok=True)

            with open(file, mode="wb") as f:
                f.write(data)

        for file, image in self.images.items():
            file = os.path.join(directory, file)
            d = os.path.dirname(file)
            os.makedirs(d, exist_ok=True)
            image.save(file)

    def provide_raw(self, name: str, raw: bytes):
        if not isinstance(raw, bytes):
            raise ValueError(raw)

        self.raw[name] = raw

    def provide_image(self, name: str, image: PIL_Image.Image):
        self.images[name] = image

    @staticmethod
    def is_valid(path: str) -> bool:
        return False

    def get_path_info(self) -> str:
        return "simulated:{}".format(self.id)

    async def is_in_path(self, path: str) -> bool:
        return path in self.raw or (path.endswith(".png") and path in self.images)

    async def read_raw(self, path: str) -> bytes:
        if path in self.raw:
            return self.raw[path]
        raise IOError("could not find {}".format(path))

    async def read_image(self, path: str) -> PIL_Image.Image:
        if path in self.raw:
            with open(shared.tmp.name + "/resource_output.png", mode="wb") as f:
                f.write(self.raw[path])
            return PIL_Image.open(shared.tmp.name + "/resource_output.png")

        return self.images[path]

    def close(self):
        self.raw.clear()
        self.images.clear()

    def get_all_entries_in_directory(
        self, directory: str, go_sub=True
    ) -> typing.Iterator[str]:
        yielded_directories = set()
        for entry in itertools.chain(list(self.raw.keys()), list(self.images.keys())):
            if entry.startswith(directory):
                if go_sub or (
                    (  # if it is an dir, same level, else one level lower
                        directory.count("/") == entry.count("/")
                        if entry.endswith("/")
                        else directory.count("/") == entry.count("/") - 1
                    )
                    and directory.count("\\") == directory.count("\\")
                ):
                    yield entry
                    d = os.path.dirname(entry)
                    if d not in yielded_directories:
                        yielded_directories.add(d)
                        yield d + "/"


# data loaders for the resource locations, SimulatedResourceLoader is not a default loader
RESOURCE_PACK_LOADERS = [
    ResourceZipFile,
    ResourceDirectory,
]
RESOURCE_LOCATIONS = []  # a list of all resource locations in the system
# todo: add manager class for this


def load_resource_packs():
    """
    Will load the resource packs found in the paths for it
    todo: add a way to add resource locations persistent to reloads
    """

    close_all_resources()

    if not os.path.exists(shared.home + "/resourcepacks"):
        os.makedirs(shared.home + "/resourcepacks")

    if shared.ENABLE_RESOURCE_PACK_LOADER:
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
        if element == "--add-resource-path":
            path = sys.argv[i + 1]
            if zipfile.is_zipfile(path):
                RESOURCE_LOCATIONS.append(ResourceZipFile(path))
            else:
                RESOURCE_LOCATIONS.append(ResourceDirectory(path))
            i += 2
        else:
            i += 1

    # for local accessing the various directories used by the game
    # todo: this might need tweaks for build executables
    RESOURCE_LOCATIONS.append(ResourceDirectory(shared.local))
    RESOURCE_LOCATIONS.append(ResourceDirectory(shared.home))
    RESOURCE_LOCATIONS.append(ResourceDirectory(shared.build))

    if shared.dev_environment:
        # only in dev-environment we need these special folders
        # todo: strip when building
        # todo: use the .jar file for source resources instead of extracting them
        RESOURCE_LOCATIONS.append(ResourceDirectory(shared.local + "/resources/main"))
        RESOURCE_LOCATIONS.append(
            ResourceDirectory(shared.local + "/resources/generated")
        )

    RESOURCE_LOCATIONS.append(ResourceZipFile(shared.local + "/source.zip"))

    shared.event_handler.call("resources:load")


def close_all_resources():
    """
    Will close all opened resource locations using <locator>.close()
    Will call the resource:close event in the process
    """
    logger.println("[RESOURCE LOADER] clearing resource system...")
    for item in RESOURCE_LOCATIONS:
        item.close()

    RESOURCE_LOCATIONS.clear()

    if shared.event_handler:
        shared.event_handler.call("resources:close")


# how mc locations look like
MC_IMAGE_LOCATIONS = [
    "block",
    "gui",
    "item",
    "entity",
    "model",
]


async def transform_name(file: str, raise_on_error=True) -> str:
    """
    Will transform an MC-ResourceLocation string into a local path
    :param file: the thing to use
    :return: the transformed
    :param raise_on_error: will raise downer exception, otherwise return the file name
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
        if file.endswith(".png"):
            logger.println(
                "can't find '{}' in resource system. Replacing with missing texture image...".format(
                    file
                )
            )
            return "assets/missing_texture.png"
        else:
            raise FileNotFoundError(file)

    return file


async def exists(file: str, transform=True):
    """
    Checks if a given file exists in the system
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
                return await x.is_in_path(file)

        return False

    for x in RESOURCE_LOCATIONS:
        if await x.is_in_path(file):
            return True

    if transform:
        try:
            return await exists(await transform_name(file), transform=False)
        except (NotImplementedError, FileNotFoundError):
            pass

    return False


async def read_raw(file: str):
    """
    Will read the content of a file in binary mode
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
            x: IResourceLoader
            if x.get_path_info() == resource:
                try:
                    return await x.read_raw(file)
                except:
                    logger.println("exception during loading file '{}'".format(file))
                    raise
        raise RuntimeError("can't find resource named {}".format(resource))

    if not await exists(file, transform=False):
        file = await transform_name(file)

    loc = RESOURCE_LOCATIONS[:]
    for x in loc:
        if await x.is_in_path(file):
            try:
                return await x.read_raw(file)
            except:
                logger.println("exception during loading file '{}'".format(file))
                raise

    raise ValueError("can't find resource '{}' in any path".format(file))


async def read_image(file: str):
    """
    Will read the content of a file in binary mode
    :param file: the file to load
    :return: the content
    """
    if file is None:
        raise ValueError(file)

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
            x: IResourceLoader
            if x.get_path_info() == resource:
                try:
                    return await x.read_image(file)
                except:
                    logger.println("exception during loading file '{}'".format(file))
                    raise

        raise RuntimeError("can't find resource named {}".format(resource))

    if not await exists(file, transform=False):
        try:
            file = await transform_name(file)
        except FileNotFoundError:
            logger.println("[WARN] could not find texture", file)
            file = "assets/missing_texture.png"

    loc = RESOURCE_LOCATIONS[:]
    for x in loc:
        if await x.is_in_path(file):
            try:
                return await x.read_image(file)

            except (SystemExit, KeyboardInterrupt):
                sys.exit(-1)
            except:
                logger.print_exception(
                    "exception during loading file '{}'".format(file)
                )

    raise ValueError("can't find resource '{}' in any path".format(file))


async def read_json(file: str):
    """
    Reads a .json file from the system
    """
    try:
        data = (await read_raw(file)).decode("utf-8")
    except:
        print("during accessing", file)
        raise

    if not data:
        raise ValueError

    try:
        return json.loads(data)
    except:
        print("during decoding", file)
        raise


async def read_pyglet_image(file):
    return mcpython.util.texture.to_pyglet_image(await read_image(file))


async def get_all_entries(directory: str) -> typing.Iterator[str]:
    """
    Will get all files & directories [ending with an "/"] of an given directory across all resource locations
    :param directory: the directory to use
    :return: a list of all found files
    """
    loc = RESOURCE_LOCATIONS
    loc.reverse()
    return itertools.chain.from_iterable(
        (x.get_all_entries_in_directory(directory) for x in loc)
    )


async def get_all_entries_special(directory: str) -> typing.Iterator[str]:
    """
    Returns all entries found with their corresponding '@<path>:<file>'-notation
    :param directory: the directory to search from
    :return: a list of found resources
    """
    return itertools.chain.from_iterable(
        map(
            lambda x: map(
                lambda s: "@{}|{}".format(x.get_path_info(), s),
                x.get_all_entries_in_directory(directory),
            ),
            RESOURCE_LOCATIONS,
        )
    )
