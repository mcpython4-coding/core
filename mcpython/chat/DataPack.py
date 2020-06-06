"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import enum
import os

import globals as G
import logger
import mcpython.ResourceLocator
import mcpython.chat.command.CommandParser
import mcpython.chat.command.McFunctionFile
import mcpython.event.EventHandler


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
    handler for data packs
    """

    def __init__(self):
        self.data_packs = []
        mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("game:close", self.cleanup)

    def _load(self):
        """
        will load all data packs
        """
        for path in os.listdir(G.local+"/datapacks"):
            self.data_packs.append(self._load_datapack(G.local+"/datapacks/"+path))
        G.eventhandler.call("datapack:search")

    def _load_datapack(self, directory: str):
        """
        will load an given data pack
        :param directory: the directory to load from
        """
        try:
            datapack = DataPack(directory)
            datapack.load()
            G.eventhandler.call("datapack:load", datapack)
            return datapack
        except:
            logger.write_exception("during loading data pack from {}".format(directory))

    def reload(self):
        """
        reloads all data packs
        """
        old_status_table = {datapack.name: datapack.status for datapack in self.data_packs}
        self.cleanup()
        self._load()
        G.eventhandler.call("datapack:reload")
        # restore old state
        for datapack in self.data_packs:
            if datapack.name in old_status_table:
                if old_status_table[datapack.name] in (DataPackStatus.ACTIVATED, DataPackStatus.DEACTIVATED):
                    datapack.status = old_status_table[datapack.name]

    def cleanup(self):
        """
        removes all data packs from the system
        """
        G.eventhandler.call("datapack:unload:pre")
        for datapack in self.data_packs: datapack.unload()
        self.data_packs.clear()
        G.eventhandler.call("datapack:unload:post")

    def try_call_function(self, name: str, info=None):
        """
        will try to invoke an function in an datapack
        :param name: the name of the function
        :param info: the info-object to use
        WARNING: will only invoke ONE function/tag from the datapacks, not all
        """
        if info is None:
            info = mcpython.chat.command.CommandParser.ParsingCommandInfo()
        if name.startswith("#"):  # an tag
            try:
                tag = G.taghandler.get_tag_for(name, "functions")
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


datapackhandler = DataPackHandler()


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
        if self.status == DataPackStatus.SYSTEM_ERROR: return
        # when the data pack was active, unload it first
        try:
            if self.status in (DataPackStatus.ACTIVATED, DataPackStatus.DEACTIVATED): self.unload()
            self.access = mcpython.ResourceLocator.ResourceDirectory(self.directory) if os.path.isdir(
                self.directory) else \
                mcpython.ResourceLocator.ResourceZipFile(self.directory)
            info = self.access.read("pack.mcmeta", "json")["pack"]
            if info["pack_format"] not in (1, 2, 3):
                self.status = DataPackStatus.ERROR
                logger.println("[DATAPACK][ERROR] datapack version '{}' can't be loaded".format(info["pack_format"]))
                return
            self.description = info["description"]
            for file in self.access.get_all_entries_in_directory("data"):
                if file.endswith("/"): continue
                split = file.split("/")
                if "function" in file:
                    name = "{}:{}".format(split[1], "/".join(split[3:]).split(".")[0])
                    self.function_table[name] = mcpython.chat.command.McFunctionFile.McFunctionFile(
                        self.access.read(file, None).decode("UTF-8"), name)
        except:
            self.status = DataPackStatus.SYSTEM_ERROR
            logger.write_exception("error during loading data pack '{}'".format(self.name))
            return
        self.status = DataPackStatus.ACTIVATED

    def unload(self):
        """
        will unload the datapack
        """
        if self.status == DataPackStatus.SYSTEM_ERROR: return
        if self.status == DataPackStatus.INACTIVE or self.status == DataPackStatus.UNLOADED:
            raise ValueError("can't un-load an not loaded datapack")
        self.status = DataPackStatus.DEACTIVATED   # deactivated access during working
        try:
            self.function_table.clear()  # unload all .mcfunction files
        except:
            self.status = DataPackStatus.SYSTEM_ERROR
            logger.write_exception("error during unloading data pack '{}'".format(self.name))
            return
        self.status = DataPackStatus.UNLOADED  # we have successfully unloaded the data-pack
        if self.access: self.access.close()  # remove access to the file system
        self.access = None  # an remove the instance

    def set_status(self, status: DataPackStatus):
        """
        sets the status of the data pack
        :param status: the status to set
        """
        if status == self.status: return
        self.status = status
        if status == DataPackStatus.ACTIVATED and self.access not in mcpython.ResourceLocator.RESOURCE_LOCATIONS:
            mcpython.ResourceLocator.RESOURCE_LOCATIONS.append(self.access)
        elif status == DataPackStatus.DEACTIVATED and self.access in mcpython.ResourceLocator.RESOURCE_LOCATIONS:
            mcpython.ResourceLocator.RESOURCE_LOCATIONS.remove(self.access)
