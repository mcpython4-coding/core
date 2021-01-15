"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import enum
import json
import os

from mcpython import shared, logger
import mcpython.ResourceLoader
import mcpython.server.command.CommandParser
import mcpython.server.command.McFunctionFile
import mcpython.common.event.EventHandler


class DataPackStatus(enum.Enum):
    """
    Enum for the loading-status of an data-pack
    """

    INACTIVE = 0  # status for every new created datapack
    ACTIVATED = 1  # the datapack is active
    DEACTIVATED = 2  # the datapack is deactivated (by the user)
    ERROR = 3  # the datapack has an error in it and can not be loaded for that reason
    UNLOADED = 4  # the datapack was unloaded and must be loaded before usage
    SYSTEM_ERROR = 5  # during loading the datapack, an internal error occurred. This datapack can't be used anymore


class DataPackHandler:
    """
    handler for datapacks
    """

    def __init__(self):
        self.data_packs = []
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "game:close", self.cleanup
        )

    def _load(self):
        """
        will load all data packs
        """
        for path in os.listdir(shared.home + "/datapacks"):
            self.data_packs.append(
                self.load_datapack_from_directory(shared.home + "/datapacks/" + path)
            )
        shared.event_handler.call("datapack:search")

    def load_datapack_from_directory(self, directory: str):
        """
        will load an given data pack
        :param directory: the directory to load from
        """
        try:
            datapack = DataPack(directory)
            datapack.load()
            shared.event_handler.call("datapack:load", datapack)
            return datapack
        except:
            logger.print_exception("during loading data pack from {}".format(directory))

    def reload(self):
        """
        reloads all data packs
        """
        old_status_table = {
            datapack.name: datapack.status for datapack in self.data_packs
        }
        self.cleanup()
        self._load()
        shared.event_handler.call("datapack:reload")
        # restore old state
        for datapack in self.data_packs:
            if datapack.name in old_status_table:
                if old_status_table[datapack.name] in (
                    DataPackStatus.ACTIVATED,
                    DataPackStatus.DEACTIVATED,
                ):
                    datapack.status = old_status_table[datapack.name]

    def cleanup(self):
        """
        removes all data packs from the system
        """
        shared.event_handler.call("datapack:unload:pre")
        for datapack in self.data_packs:
            datapack.unload()
        self.data_packs.clear()
        shared.event_handler.call("datapack:unload:post")

    def try_call_function(
        self,
        name: str,
        info: mcpython.server.command.CommandParser.ParsingCommandInfo = None,
    ):
        """
        Will try to invoke an function in an datapack
        :param name: the name of the function, e.g. minecraft:test
        :param info: the info-object to use
        WARNING: will only invoke ONE function/tag from the datapacks, not all
        """
        if info is None:
            info = mcpython.server.command.CommandParser.ParsingCommandInfo()
        if name.startswith("#"):  # an tag
            try:
                tag = shared.tag_handler.get_tag_for(name, "functions")
            except ValueError:
                return
            for name in tag.entries:
                self.try_call_function(name, info.copy())
            return
        for datapack in self.data_packs:
            if datapack.status == DataPackStatus.ACTIVATED:
                if name in datapack.function_table:
                    return datapack.function_table[name].execute(info)
        raise ValueError("can't find function '{}'".format(name))


datapack_handler = DataPackHandler()


class DataPack:
    """
    class for an single data pack
    """

    def __init__(self, directory: str):
        """
        will create an new DataPack-object
        :param directory: where the datapack is located
        """
        self.directory = directory
        self.function_table = {}
        self.status = DataPackStatus.INACTIVE
        self.name = directory.split("/")[-1].split("\\")[-1]
        self.access = None
        self.description = ""

    def load(self):
        """
        will load the data pack
        """
        if self.status == DataPackStatus.SYSTEM_ERROR:
            return
        # when the data pack was active, unload it first
        try:
            if self.status in (DataPackStatus.ACTIVATED, DataPackStatus.DEACTIVATED):
                self.unload()
            self.access = (
                mcpython.ResourceLoader.ResourceDirectory(self.directory)
                if os.path.isdir(self.directory)
                else mcpython.ResourceLoader.ResourceZipFile(self.directory)
            )
            info = json.loads(self.access.read_raw("pack.mcmeta").decode("utf-8"))[
                "pack"
            ]
            if info["pack_format"] not in (1, 2, 3):
                self.status = DataPackStatus.ERROR
                logger.println(
                    "[DATAPACK][ERROR] datapack version '{}' can't be loaded".format(
                        info["pack_format"]
                    )
                )
                return
            self.description = info["description"]
            for file in self.access.get_all_entries_in_directory("data"):
                if file.endswith("/"):
                    continue
                split = file.split("/")
                if "function" in file:
                    name = "{}:{}".format(split[1], "/".join(split[3:]).split(".")[0])
                    self.function_table[
                        name
                    ] = mcpython.server.command.McFunctionFile.McFunctionFile(
                        self.access.read_raw(file).decode("UTF-8"), name
                    )
        except:
            self.status = DataPackStatus.SYSTEM_ERROR
            logger.print_exception(
                "error during loading data pack '{}'".format(self.name)
            )
            return
        self.status = DataPackStatus.ACTIVATED

    def unload(self):
        """
        will unload the datapack
        """
        if self.status == DataPackStatus.SYSTEM_ERROR:
            return
        if (
            self.status == DataPackStatus.INACTIVE
            or self.status == DataPackStatus.UNLOADED
        ):
            raise ValueError("can't un-load an not loaded datapack")
        self.status = DataPackStatus.DEACTIVATED  # deactivated access during working
        try:
            self.function_table.clear()  # unload all .mcfunction files
        except:
            self.status = DataPackStatus.SYSTEM_ERROR
            logger.print_exception(
                "error during unloading data pack '{}'".format(self.name)
            )
            return
        self.status = (
            DataPackStatus.UNLOADED
        )  # we have successfully unloaded the data-pack
        if self.access:
            self.access.close()  # remove access to the file system
        self.access = None  # an remove the instance

    def set_status(self, status: DataPackStatus):
        """
        sets the status of the data pack
        :param status: the status to set
        """
        if status == self.status:
            return
        self.status = status
        if (
            status == DataPackStatus.ACTIVATED
            and self.access not in mcpython.ResourceLoader.RESOURCE_LOCATIONS
        ):
            mcpython.ResourceLoader.RESOURCE_LOCATIONS.append(self.access)
        elif (
            status == DataPackStatus.DEACTIVATED
            and self.access in mcpython.ResourceLoader.RESOURCE_LOCATIONS
        ):
            mcpython.ResourceLoader.RESOURCE_LOCATIONS.remove(self.access)
