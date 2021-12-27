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
import importlib
import json
import os
import sys
import time
import typing
import zipfile
from abc import ABC

import mcpython.common.config
import mcpython.common.mod.ExtensionPoint
import mcpython.common.mod.Mod
import mcpython.common.mod.ModLoadingStages
import mcpython.engine.ResourceLoader
import mcpython.util.math
import toml
from mcpython import shared
from mcpython.common.mod.util import LoadingInterruptException
from mcpython.engine import logger


def cast_dependency(dependency: dict) -> mcpython.common.mod.Mod.ModDependency:
    """
    Will cast a dict-structure to the dependency
    :param dependency: the dependency dict describing the data
    :return: the parsed mod.Mod.ModDependency-object
    """
    config = {}

    if "version" in dependency:
        config["version_min"] = dependency["version"]

    if "upper_version" in dependency:
        config["version_max"] = dependency["upper_version"]

    if "versions" in dependency:
        config["versions"] = dependency["versions"]

    return mcpython.common.mod.Mod.ModDependency(dependency["name"], **config)


def parse_provider_json(container: "ModContainer", data: dict):
    """
    Parser for the provider.json information file mods and other containers are
    allowed to provide in order to do stuff before mod loading
    """

    if "importDirect" in data:
        for module in data["importDirect"]:
            try:
                importlib.import_module(module)
            except:
                logger.print_exception(
                    f"[MOD DISCOVERY][ERROR] failed to load module {module} for container {container} in early loading phase"
                )


class ModContainer:
    """
    Class holding information about a mod file/directory
    (Not a single mod, but more a load location)

    Is similar to sys.path-entries, but only for mods
    """

    def __init__(self, path: str):
        self.path = path
        self.assigned_mod_loader: typing.Optional[AbstractModLoaderInstance] = None

        if zipfile.is_zipfile(path):
            self.resource_access = mcpython.engine.ResourceLoader.ResourceZipFile(
                path, close_when_scheduled=False
            )
            sys.path.append(path)

        elif os.path.isdir(path):
            self.resource_access = mcpython.engine.ResourceLoader.ResourceDirectory(
                path
            )
            sys.path.append(path)

        elif os.path.isfile(path):
            # In this case, it is a file, so we know what mod loader to use
            self.resource_access = (
                mcpython.engine.ResourceLoader.SimulatedResourceLoader()
            )
            self.assigned_mod_loader = PyFileModLoader(self)
            self.assigned_mod_loader.on_select()

        else:
            raise RuntimeError(f"Invalid mod source file: {path}")

        import mcpython.engine.event.EventHandler as EventHandler

        EventHandler.PUBLIC_EVENT_BUS.subscribe("resources:load", self.add_resources)
        self.add_resources()

        self.loaded_mods = []

    def add_resources(self):
        mcpython.engine.ResourceLoader.RESOURCE_LOCATIONS.append(self.resource_access)

    def try_identify_mod_loader(self):
        """
        Does some lookup for identifying the mod loader
        """
        if self.assigned_mod_loader is not None:
            return

        for loader in ModLoader.KNOWN_MOD_LOADERS:
            if loader.match_container_loader(self):
                self.assigned_mod_loader = loader(self)
                break
        else:
            logger.println(
                f"[MOD LOADER][WARN] could not identify mod loader for mod {self}"
            )
            return

        self.assigned_mod_loader.on_select()

    def load_meta_files(self):
        """
        Looks out for some meta files
        """
        # this file allows some special stuff to happen before real loading stuff
        if self.resource_access.is_in_path("provider.json"):
            parse_provider_json(
                self,
                json.loads(
                    self.resource_access.read_raw("provider.json").decode("utf-8")
                ),
            )

    def __repr__(self):
        return f"ModContainer(path='{self.path}',loader={self.assigned_mod_loader})"


class AbstractModLoaderInstance(ABC):
    @classmethod
    def match_container_loader(cls, container: ModContainer) -> bool:
        return False

    def __init__(self, container: ModContainer):
        self.container = container
        self.parent = None
        self.raw_data = None

    def on_select(self):
        """
        Informal method called sometime after construction
        """

    def on_instance_bake(self, mod: mcpython.common.mod.Mod):
        pass


class PyFileModLoader(AbstractModLoaderInstance):
    pass


class DefaultModJsonBasedLoader(AbstractModLoaderInstance):
    @classmethod
    def match_container_loader(cls, container: ModContainer) -> bool:
        return container.resource_access.is_in_path("mods.json")

    def on_select(self):
        data = json.loads(
            self.container.resource_access.read_raw("mods.json").decode("utf-8")
        )

        self.raw_data = data
        self.load_from_data(data)

    def load_from_data(self, data):

        version = data["version"]
        if version == "1.2.0":  # latest
            for entry in data["entries"]:
                if "name" not in entry:
                    shared.mod_loader.error_builder.println(
                        "- invalid entry in '{}' (entry: {}): missing entry-tag".format(
                            self.container, entry
                        )
                    )
                    continue

                modname = entry["name"]
                loader = entry["loader"] if "loader" in entry else "python:default"
                if loader == "python:default":
                    if "version" not in entry:
                        shared.mod_loader.error_builder.println(
                            "- invalid entry found in '{}' (mod: {]): missing 'version'-entry".format(
                                self.container, modname
                            )
                        )
                        continue

                    version = tuple([int(e) for e in entry["version"].split(".")])
                    instance = mcpython.common.mod.Mod.Mod(modname, version)

                    if "depends" in entry:
                        for depend in entry["depends"]:
                            t = None if "type" not in depend else depend["type"]
                            if t is None or t == "depend":
                                instance.add_dependency(cast_dependency(depend))
                            elif t == "depend_not_load_order":
                                instance.add_not_load_dependency(
                                    cast_dependency(depend)
                                )
                            elif t == "not_compatible":
                                instance.add_not_compatible(cast_dependency(depend))
                            elif t == "load_before":
                                instance.add_load_before_if_arrival(
                                    cast_dependency(depend)
                                )
                            elif t == "load_after":
                                instance.add_load_after_if_arrival(
                                    cast_dependency(depend)
                                )
                            elif t == "only_if":
                                instance.add_load_only_when_arrival(
                                    cast_dependency(depend)
                                )
                            elif t == "only_if_not":
                                instance.add_load_only_when_not_arrival(
                                    cast_dependency(depend)
                                )

                    if "load_resources" in entry and entry["load_resources"]:
                        instance.add_load_default_resources()

                    for location in entry["load_files"]:
                        try:
                            importlib.import_module(
                                location.replace("/", ".").replace("\\", ".")
                            )
                        except ModuleNotFoundError:
                            shared.mod_loader.error_builder.println(
                                "- can't load mod file {}".format(location)
                            )
                            return
                elif loader in ModLoader.JSON_LOADERS:
                    mod_loader = ModLoader.JSON_LOADERS[loader](self.container)
                    mod_loader.parent = self
                    mod_loader.on_select()
                else:
                    shared.mod_loader.error_builder.println(
                        f"mod version file {self.container} specified dependency on mod loader {loader}, which is not arrival!"
                    )
        else:
            raise IOError("invalid version: {}".format(version))


class TomlModLoader(DefaultModJsonBasedLoader):
    @classmethod
    def match_container_loader(cls, container: ModContainer) -> bool:
        return container.resource_access.is_in_path(
            "mods.toml"
        ) or container.resource_access.is_in_path("META-INF/mods.toml")

    def on_select(self):
        if self.container.resource_access.is_in_path("mods.toml"):
            data = self.container.resource_access.read_raw("mods.toml")
        else:
            data = self.container.resource_access.read_raw("META-INF/mods.toml")

        try:
            data = toml.loads(data.decode("utf-8"))
        except:
            raise RuntimeError(self.container)

        self.raw_data = data
        self.load_from_data(data)

    def load_from_data(self, data):
        if "modLoader" in data:
            if data["modLoader"] != "pythonml":
                loader = data["modLoader"]

                if loader in ModLoader.TOML_LOADERS:
                    mod_loader = ModLoader.TOML_LOADERS[loader](self.container)
                    mod_loader.parent = self
                    try:
                        mod_loader.on_select()
                    except:
                        logger.print_exception(
                            f"during decoding container {self.container}"
                        )
                    else:
                        self.container.assigned_mod_loader = mod_loader
                else:
                    shared.mod_loader.error_builder.println(
                        "- found mod-loader requirement '{}' in {}, which is not supported in this env".format(
                            loader, self.container
                        )
                    )
                return

        if "loaderVersion" in data:
            if data["loaderVersion"].startswith("["):
                shared.mod_loader.error_builder.println(
                    "- found forge-version indicator in mod from {}, which is currently unsupported".format(
                        self.container
                    )
                )
                return

            version = data["loaderVersion"]

            if version.endswith("["):
                mc_version = 0  # todo: implement
            elif version.count("[") == version.count("]") == 0:
                mc_version = version.split("|")
            else:
                shared.mod_loader.error_builder.println(
                    "[SOURCE][FATAL] can't decode version id '{}' in container {]".format(
                        version, self.container
                    )
                )
                return
        else:
            mc_version = None

        super().load_from_data(
            {"main files": [e["importable"] for e in data["main_files"]]}
        )

        for instance in shared.mod_loader.located_mod_instances:
            instance.add_dependency(
                mcpython.common.mod.Mod.ModDependency("minecraft", mc_version)
            )

        for modname in data["dependencies"]:
            for dependency in data["dependencies"][modname]:
                name = dependency["modId"]
                if name != "forge":
                    shared.mod_loader.mods[modname].add_dependency(name)
                    # todo: add version of mod


class ModLoader:
    """
    The ModLoader class

    The mod loader is a system capable of loading code into the game, for actively modification
    the behaviour and the content of the game.

    WARNING: mods CAN damage your pc software-wise. They are small programs executed on your pc.
        Use only mods from sources you trust!
        DO  N E V E R  DOWNLOAD MODS FROM STRANGE SOURCES
        We, the developers of mcpython, give NOT WARRANTIES for things mods do, including, but not limited to,
        damage on the end user pc and/or direct or indirect stealing of valuable information about the user, including
        the download of programs to do so.
    """

    # This stores a list of valid mod loader classes used during discovery
    KNOWN_MOD_LOADERS: typing.List[typing.Type[AbstractModLoaderInstance]] = [
        PyFileModLoader,
        DefaultModJsonBasedLoader,
        TomlModLoader,
    ]

    # The real LOADER-extensions,
    JSON_LOADERS: typing.Dict[str, typing.Type[AbstractModLoaderInstance]] = {}
    TOML_LOADERS: typing.Dict[str, typing.Type[AbstractModLoaderInstance]] = {}

    def __init__(self):
        """
        Creates a new mod-loader-instance
        WARNING: only ONE instance should be present, otherwise, bad things might happen
        """
        self.found_mod_files: typing.Set[str] = set()
        self.mod_containers: typing.List[ModContainer] = []

        # the list of located mods
        self.located_mods: typing.List[mcpython.common.mod.Mod.Mod] = []

        # a mapping mod name -> mod instance
        self.mods: typing.Dict[str, mcpython.common.mod.Mod.Mod] = {}

        # the order of mod loading, by mod name
        self.mod_loading_order: typing.List[str] = []

        # the directory currently loading from
        self.active_directory: typing.Optional[str] = None
        self.current_container: typing.Optional[ModContainer] = None

        # which stage we are in
        self.active_loading_stage: int = 0

        # used for detecting mod changes between versions
        self.previous_mod_list = {}

        # temporary list of mods, for setting stuff
        self.located_mod_instances = []

        # fill the previous mods with data from the disk, if arrival
        if os.path.exists(shared.build + "/mods.json"):
            with open(shared.build + "/mods.json") as f:
                self.previous_mod_list = json.load(f)

        # if mod loading has finished
        self.finished = False

        self.error_builder = logger.TableBuilder()

    def __call__(
        self, modname: str, event_name: str, *args, **kwargs
    ) -> typing.Callable[
        [typing.Callable | typing.Awaitable], typing.Callable | typing.Awaitable
    ]:
        """
        Annotation to the event system
        :param modname: the mod name
        :param event_name: the event name
        :param info: the info, as shown by EventBus during errors
        :return: a callable, used for regisering

        Example:
        @shared.mod_loader("minecraft", "stage:mod:init")
        def test():
            print("Hello world!")

        Will wrap the target around an async method if needed
        """

        def annotate(target):
            if not isinstance(target, typing.Awaitable):

                async def wrap(*args2, **kwargs2):
                    result = target(*args, *args2)
                    if isinstance(result, typing.Awaitable):
                        result = await result
                    return result

                self.mods[modname].eventbus.subscribe(
                    event_name, wrap(), *args, **kwargs
                )
            else:
                self.mods[modname].eventbus.subscribe(
                    event_name, target, *args, **kwargs
                )
            return target

        return annotate

    def __getitem__(self, item: str):
        if item in self.mods:
            return self.mods[item]

        raise IndexError(item)

    def __contains__(self, item: str):
        return item in self.mods

    def __iter__(self):
        return self.mods.values()

    def look_for_mod_files(self):
        """
        Scanner for mod files, parsing the parsed sys.argv stuff

        Stores the result in the found_mod_files attribute of this
        """

        folders = [shared.home + "/mods"]

        for entry in shared.launch_wrapper.get_flag_status("add-mod-dir", default=[]):
            folders += entry

        files = set(
            sum(
                [
                    [os.path.join(loc, file) for file in os.listdir(loc)]
                    for loc in folders
                    if os.path.exists(loc)
                ],
                [],
            )
        )

        for entry in shared.launch_wrapper.get_flag_status("add-mod-file", default=[]):
            files |= set(entry)

        for entry in shared.launch_wrapper.get_flag_status(
            "remove-mod-file", default=[]
        ):
            files.difference_update(set(entry))

        # todo: escape logging here

        self.found_mod_files |= files

    def parse_mod_files(self):
        containers = [ModContainer(path) for path in self.found_mod_files]
        self.mod_containers += containers

        for container in containers[:]:
            self.current_container = container
            try:
                container.try_identify_mod_loader()
            except:
                logger.print_exception(container)
                containers.remove(container)

        for container in containers[:]:
            try:
                self.current_container = container
                container.load_meta_files()
            except:
                logger.print_exception(container)
                containers.remove(container)

    def check_errors(self):
        if self.error_builder.areas[-1]:
            self.error_builder.finish()
            raise RuntimeError()

    def load_missing_mods(self):
        for container in self.mod_containers[:]:
            if container.assigned_mod_loader is None:
                self.current_container = container
                container.try_identify_mod_loader()

                if container.assigned_mod_loader is not None:
                    container.load_meta_files()
                else:
                    self.mod_containers.remove(container)

        logger.println(
            "found mod{}: {}".format(
                "s" if len(self.located_mods) > 1 else "", len(self.located_mods)
            )
        )

    def check_for_updates(self):
        """
        Will check for changes between versions between this session and the one before

        In case of a change, rebuild mode is entered

        todo: add a way for mods to decide if a rebuild is needed when they are added / removed
        """

        for modname in self.previous_mod_list.keys():
            if modname not in self.mods or self.mods[modname].version != tuple(
                self.previous_mod_list[modname]
            ):
                # we have an mod which was previous loaded and not now or which was loaded before in another version
                # todo: include version change
                logger.println(
                    "rebuild mode due to mod change ({}) of '{}'".format(
                        "remove" if modname not in self.mods else "version change",
                        modname,
                    )
                )
                shared.invalidate_cache = True

        for modname in self.mods.keys():
            if modname not in self.previous_mod_list:  # any new mods?
                # we have an mod which was loaded not previous but now
                # todo: include version of the mod
                logger.println(
                    "rebuild mode due to mod change (addition) of '{}'".format(modname)
                )
                shared.invalidate_cache = True

    def write_mod_info(self):
        """
        Writes the data for the mod table into the file
        """
        os.makedirs(shared.build, exist_ok=True)

        with open(shared.build + "/mods.json", mode="w") as f:
            m = {instance.name: instance.version for instance in self.mods.values()}
            json.dump(m, f)
        return self

    def add_to_add(self, instance: mcpython.common.mod.Mod.Mod):
        """
        Will add a mod-instance into the inner system
        :param instance: the mod instance to add
        Use only when really needed. The system is designed for being data-driven, and things might go wrong
            when manually doing this
        """
        if not shared.event_handler.call_cancelable(
            "modloader:mod_registered", instance
        ):
            return

        self.mods[instance.name] = instance
        self.located_mods.append(instance)

        if instance.path is not None:
            instance.container = self.current_container
            instance.resource_access = self.current_container.resource_access
            instance.path = self.current_container.path
            self.current_container.assigned_mod_loader.on_instance_bake(instance)

        self.located_mod_instances.append(instance)

        return self

    def check_mod_duplicates(self):
        """
        Will check for mod duplicates
        :return an tuple of errors as string and collected mod-info's as dict
        todo: add config option for strategy: fail, load newest, load oldest, [load all}, load none
        """
        errors = False
        mod_info = {}

        for mod in self.located_mods:
            if mod.name in mod_info:
                self.error_builder.println(
                    " - Mod '{}' found in {} has more than one version in the folder. Please add every mod only ones!".format(
                        mod.name,
                        mod.path,
                    )
                )
                errors = True
                shared.event_handler.call(
                    "minecraft:mod_loader:duplicated_mod_found", self, mod
                )
            else:
                mod_info[mod.name] = []

        return errors, mod_info

    def check_dependency_errors(self, errors: bool, mod_info: dict):
        """
        Will iterate through all mods and check dependencies
        :param errors: if errors occurred
        :param mod_info: the mod info dict
        :return: errors and mod-info-tuple
        """
        for mod in self.located_mods:
            if not mod.check_dependencies(self, mod_info):
                errors = True

        return errors, mod_info

    def sort_mods(self):
        """
        Will create the mod-order-list by sorting after dependencies
        todo: use build-in library
        """
        errors, mod_info = self.check_dependency_errors(*self.check_mod_duplicates())
        for mod in self.located_mods:
            for depend in mod.depend_info[4]:
                if mod.name in mod_info and depend.name not in mod_info[mod.name]:
                    mod_info[mod.name].append(depend.name)
            for depend in mod.depend_info[3]:
                if depend.name in mod_info and mod.name not in mod_info[depend.name]:
                    mod_info[depend.name].append(mod.name)

        if errors:
            logger.println("found mods: ")
            for instance in self.mods.values():
                logger.println(" -", instance.mod_string())
            logger.println()

            self.error_builder.finish()
            print("closing")
            sys.exit(-1)

        self.mod_loading_order = list(
            mcpython.util.math.topological_sort(
                [(key, mod_info[key]) for key in mod_info.keys()]
            )
        )

        self.check_errors()
        logger.write_into_container(
            [
                " - {}".format(self.mods[name].mod_string())
                for name in self.mod_loading_order
            ]
        )

    async def process(self):
        """
        Will process some loading tasks scheduled
        Used internally during mod loading state
        If on client, the renderer is also updated
        """
        if not mcpython.common.mod.ModLoadingStages.manager.order.is_active():
            return

        astate = shared.state_handler.active_state
        astate.parts[0].progress_max = len(
            mcpython.common.mod.ModLoadingStages.manager.stages
        )
        astate.parts[1].progress_max = len(self.mods)

        start = time.time()
        while time.time() - start < 0.2:
            stage = mcpython.common.mod.ModLoadingStages.manager.get_stage()
            if stage is None:
                break

            try:
                if await stage.call_one(astate):
                    return

            except (SystemExit, KeyboardInterrupt):
                raise

            except LoadingInterruptException:
                print("stopping loading cycle")
                return

            except:
                logger.print_exception()
                sys.exit(-1)

        # if shared.IS_CLIENT:
        self.update_pgb_text()

    def update_pgb_text(self):
        """
        Will update the text of the pgb's in mod loading
        """
        stage = mcpython.common.mod.ModLoadingStages.manager.get_stage()
        if stage is None:
            return

        astate = shared.state_handler.active_state
        instance = self.mods[self.mod_loading_order[stage.active_mod_index]]

        if (
            stage.active_event in instance.eventbus.event_subscriptions
            and len(instance.eventbus.event_subscriptions[stage.active_event]) > 0
        ):
            f, text = instance.eventbus.event_subscriptions[stage.active_event][0]
        else:
            f, text = None, ""

        astate.parts[2].text = text if text is not None else "function {}".format(f)
        astate.parts[1].text = "{} ({}/{})".format(
            instance.name, stage.active_mod_index + 1, len(self.mods)
        )
        astate.parts[1].progress = stage.active_mod_index + 1
        astate.parts[0].text = "{} ({}/{}) in {} ({}/{})".format(
            stage.active_event,
            stage.current_progress,
            len(stage.events),
            stage.name,
            self.active_loading_stage + 1,
            len(mcpython.common.mod.ModLoadingStages.manager.stages),
        )


shared.mod_loader = ModLoader()
