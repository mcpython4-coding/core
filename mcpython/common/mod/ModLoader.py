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

import mcpython.client.state.StateModLoading
import mcpython.common.config
import mcpython.common.event.EventHandler
import mcpython.common.ExtensionPoint
import mcpython.common.mod.Mod
import mcpython.common.mod.ModLoadingStages
import mcpython.ResourceLoader
import mcpython.util.math
import toml
from mcpython import logger, shared


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

    def __init__(self):
        """
        Creates a new mod-loader-instance
        WARNING: only ONE instance should be present, otherwise, bad things might happen
        """
        # the list of located mods
        self.located_mods: typing.List[mcpython.common.mod.Mod.Mod] = []

        # a mapping mod name -> mod instance
        self.mods: typing.Dict[str, mcpython.common.mod.Mod.Mod] = {}

        # the order of mod loading, by mod name
        self.mod_loading_order: typing.List[str] = []

        # the directory currently loading from
        self.active_directory: typing.Optional[str] = None

        # which stage we are in
        self.active_loading_stage: int = 0

        # used for detecting mod changes between versions
        self.previous_mods = {}

        # temporary list of mods, for setting stuff
        self.located_mod_instances = []

        # fill the previous mods with data from the disk, if arrival
        if os.path.exists(shared.build + "/mods.json"):
            with open(shared.build + "/mods.json") as f:
                self.previous_mods = json.load(f)

        # if mod loading has finished
        self.finished = False

        # the stages used during reload, todo: remove
        self.reload_stages: typing.List[str] = []

        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "command:reload:end", self.execute_reload_stages
        )

        self.error_builder = logger.TableBuilder()

    def register_reload_assigned_loading_stage(self, stage: str):
        """
        Will register an loading stage as one to executed on every reload
        :param stage: the event name of the stage
        todo: remove -> resource pipe
        """
        self.reload_stages.append(stage)
        return self

    def execute_reload_stages(self):
        # todo: remove -> resource pipe
        for event_name in self.reload_stages:
            for i in range(len(self.mods)):
                instance = shared.mod_loader.mods[
                    shared.mod_loader.mod_loading_order[i]
                ]
                instance.eventbus.resetEventStack(event_name)
                instance.eventbus.call(event_name)
        return self

    def __call__(
        self, modname: str, event_name: str, *args, **kwargs
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """
        Annotation to the event system
        :param modname: the mod name
        :param event_name: the event name
        :param info: the info
        :return: an ModLoaderAnnotation-instance for annotation
        """
        return lambda function: self.mods[modname].eventbus.subscribe(
            event_name, function, *args, **kwargs
        )

    def __getitem__(self, item: str):
        if item in self.mods:
            return self.mods[item]
        raise IndexError(item)

    def __contains__(self, item: str):
        return item in self.mods

    def __iter__(self):
        return self.mods.values()

    def get_locations(self) -> list:
        """
        Will return an list of mod locations found for loading
        todo: split up into smaller portions
        """
        locations = []
        folders = [shared.home + "/mods"]
        i = 0

        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--add-mod-dir":
                folders.append(sys.argv[i + 1])
                for _ in range(2):
                    sys.argv.pop(i)
                sys.path.append(folders[-1])
            elif element == "--add-mod-file":
                locations.append(sys.argv[i + 1])
                for _ in range(2):
                    sys.argv.pop(i)
            else:
                i += 1

        for loc in folders:
            locations += [os.path.join(loc, x) for x in os.listdir(loc)]

        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--remove-mod-file":
                file = sys.argv[i + 1]
                if file in locations:
                    locations.remove(file)
                else:
                    self.error_builder.println(
                        "- attempted to remove mod '{}' which is not found".format(file)
                    )
                for _ in range(2):
                    sys.argv.pop(i)
            else:
                i += 1

        for i, location in enumerate(locations):
            logger.ESCAPE[location.replace("\\", "/")] = "%MOD:{}%".format(i + 1)

        return locations

    def load_mod_json_from_locations(self, locations: typing.List[str]):
        """
        Will load the mod description files for the given locations and parse their content
        :param locations: the locations found
        """
        self.located_mod_instances.clear()

        for file in locations:
            if os.path.isfile(file):
                if zipfile.is_zipfile(file):  # compressed file
                    sys.path.append(file)
                    mcpython.ResourceLoader.RESOURCE_LOCATIONS.insert(
                        0, mcpython.ResourceLoader.ResourceZipFile(file)
                    )
                    self.active_directory = file
                    with zipfile.ZipFile(file) as f:
                        try:
                            with f.open("mod.json", mode="r") as sf:
                                self.load_mods_json(sf.read().decode("utf-8"), file)
                        except KeyError:
                            try:
                                with f.open("mod.toml", mode="r") as sf:
                                    self.load_mods_toml(sf.read().decode("utf-8"), file)
                            except KeyError:
                                self.error_builder.println(
                                    "- could not locate mod.json file in mod at '{}'".format(
                                        file
                                    )
                                )

                elif file.endswith(".py"):  # python script file
                    self.active_directory = file
                    try:
                        data = importlib.import_module(
                            "mods." + file.split("/")[-1].split("\\")[-1].split(".")[0]
                        )
                    except ModuleNotFoundError:
                        data = importlib.import_module(
                            file.split("/")[-1].split("\\")[-1].split(".")[0]
                        )
                    for instance in self.located_mod_instances:
                        instance.package = data

            elif os.path.isdir(file) and "__pycache__" not in file:  # source directory
                sys.path.append(file)
                mcpython.ResourceLoader.RESOURCE_LOCATIONS.insert(
                    0, mcpython.ResourceLoader.ResourceDirectory(file)
                )
                self.active_directory = file
                if os.path.exists(file + "/mod.json"):
                    with open(file + "/mod.json") as sf:
                        content = sf.read()
                    try:
                        self.load_mods_json(content, file + "/mod.json")
                    except:
                        logger.print_exception(
                            f"during loading mod.json file from '{file}'"
                        )

                elif os.path.exists(file + "/mods.toml"):
                    with open(file + "/mods.toml") as sf:
                        self.load_mods_toml(sf.read(), file + "/mods.toml")
                else:
                    self.error_builder.println(
                        "- could not locate mod.json file for mod for mod-directory '{}'".format(
                            file
                        )
                    )

            for mod in self.located_mod_instances:
                mod.path = file
            self.located_mod_instances.clear()

    def look_out(self, from_files=True):
        """
        Will load all mods arrival
        """
        if from_files:
            locations = self.get_locations()

            shared.event_handler.call(
                "minecraft:modloader:location_lookup_complete", self, locations
            )

            self.load_mod_json_from_locations(locations)

        # this is special, as it is not loaded from files...
        import mcpython.common.mod.ModMcpython

        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]

            if element == "--remove-mod":
                name = sys.argv[i + 1]

                if name in self.mods:
                    del self.mods[name]
                else:
                    self.error_builder.println(
                        "- attempted to remove mod '{}' which is not arrival".format(
                            name
                        )
                    )

                for _ in range(2):
                    sys.argv.pop(i)

            else:
                i += 1

        logger.println(
            "found mod{}: {}".format(
                "s" if len(self.located_mods) > 1 else "", len(self.located_mods)
            )
        )

        shared.event_handler.call(
            "minecraft:modloader:mod_selection_complete", self, self.mods
        )

        self.check_for_update()

    def check_for_update(self):
        """
        Will check for changes between versions between this session and the one before
        """
        for modname in self.previous_mods.keys():
            if modname not in self.mods or self.mods[modname].version != tuple(
                self.previous_mods[modname]
            ):
                # we have an mod which was previous loaded and not now or which was loaded before in another version
                # todo: include version change
                logger.println(
                    "rebuild mode due to mod change (remove / version change) of '{}'".format(
                        modname
                    )
                )
                if shared.event_handler.call_cancelable(
                    "minecraft:modloader:mod_change", self, modname, self.mods[modname]
                ):
                    shared.invalidate_cache = True

        for modname in self.mods.keys():
            if modname not in self.previous_mods:  # any new mods?
                # we have an mod which was loaded not previous but now
                # todo: include version of the mod
                logger.println(
                    "rebuild mode due to mod change (addition) of '{}'".format(modname)
                )
                if shared.event_handler.call_cancelable(
                    "minecraft:modloader:mod_addition",
                    self,
                    modname,
                    self.mods[modname],
                ):
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

    def load_mods_json(self, data: str, file: str):
        """
        Will parse the data to the correct system
        :param data: the data to load
        :param file: the file located under
        """
        self.load_from_decoded_json(json.loads(data), file)
        return self

    def load_from_decoded_json(self, data: dict, file: str):
        """
        Will parse the decoded json-data to the correct system
        :param data: the data of the mod
        :param file: the file allocated (used for warning messages)
        todo: maybe a better format?
        """
        version = data["version"]
        if version == "1.2.0":  # latest
            """
            example:
            {
                "version": "1.2.0",
                "entries": [
                    {
                        "name": "TestMod",
                        "version": "Some.Version",
                        "load_resources": true,
                        "load_files": ["some.package.to.load"]
                    }
                ]
            }
            """
            for entry in data["entries"]:
                if "name" not in entry:
                    self.error_builder.println(
                        "- invalid entry in '{}' (entry: {}): missing entry-tag".format(
                            file, entry
                        )
                    )
                    continue

                modname = entry["name"]
                loader = entry["loader"] if "loader" in entry else "python:default"
                if loader == "python:default":
                    if "version" not in entry:
                        self.error_builder.println(
                            "- invalid entry found in '{}': missing 'version'-entry".format(
                                file
                            )
                        )
                        continue

                    version = tuple([int(e) for e in entry["version"].split(".")])
                    instance = mcpython.common.mod.Mod.Mod(modname, version)

                    if "depends" in entry:
                        for depend in entry["depends"]:
                            t = None if "type" not in depend else depend["type"]
                            if t is None or t == "depend":
                                instance.add_dependency(self.cast_dependency(depend))
                            elif t == "depend_not_load_order":
                                instance.add_not_load_dependency(
                                    self.cast_dependency(depend)
                                )
                            elif t == "not_compatible":
                                instance.add_not_compatible(
                                    self.cast_dependency(depend)
                                )
                            elif t == "load_before":
                                instance.add_load_before_if_arrival(
                                    self.cast_dependency(depend)
                                )
                            elif t == "load_after":
                                instance.add_load_after_if_arrival(
                                    self.cast_dependency(depend)
                                )
                            elif t == "only_if":
                                instance.add_load_only_when_arrival(
                                    self.cast_dependency(depend)
                                )
                            elif t == "only_if_not":
                                instance.add_load_only_when_not_arrival(
                                    self.cast_dependency(depend)
                                )

                    if "load_resources" in entry and entry["load_resources"]:
                        instance.add_load_default_resources()

                    for location in entry["load_files"]:
                        try:
                            importlib.import_module(
                                location.replace("/", ".").replace("\\", ".")
                            )
                        except ModuleNotFoundError:
                            self.error_builder.println(
                                "- can't load mod file {}".format(location)
                            )
                            return
                elif (
                    loader
                    in mcpython.common.ExtensionPoint.ModLoaderExtensionPoint.EXTENSION_POINTS[
                        0
                    ]
                ):
                    mcpython.common.ExtensionPoint.ModLoaderExtensionPoint.EXTENSION_POINTS[
                        0
                    ][
                        loader
                    ].load_mod_from_json(
                        entry
                    )
                else:
                    self.error_builder.println(
                        f"mod version file {file} specified dependency on mod loader {loader}, which is not arrival!"
                    )
        else:
            raise IOError("invalid version: {}".format(version))

    @classmethod
    def cast_dependency(cls, depend: dict):
        """
        will cast an dict-structure to the depend
        :param depend: the depend dict
        :return: the parsed mod.Mod.ModDependency-object
        """
        config = {}

        if "version" in depend:
            config["version_min"] = depend["version"]

        if "upper_version" in depend:
            config["version_max"] = depend["upper_version"]

        if "versions" in depend:
            config["versions"] = depend["versions"]

        return mcpython.common.mod.Mod.ModDependency(depend["name"], **config)

    def load_mods_toml(self, data: str, file: str):
        """
        Will load a toml-data-object
        :param data: the toml-representation
        :param file: the file for debugging reasons
        """
        data = toml.loads(data)
        if "modLoader" in data:
            if data["modLoader"] != "pythonml":
                loader = data["modLoader"]

                if (
                    loader
                    in mcpython.common.ExtensionPoint.ModLoaderExtensionPoint.EXTENSION_POINTS[
                        1
                    ]
                ):
                    mcpython.common.ExtensionPoint.ModLoaderExtensionPoint.EXTENSION_POINTS[
                        1
                    ][
                        loader
                    ].load_mod_from_toml(
                        data
                    )
                else:
                    self.error_builder.println(
                        "- found {} in file {}. As an mod-author, please upgrade to python (pythonml) or install a loader extension mod".format(
                            loader, file
                        )
                    )
                return

        if "loaderVersion" in data:
            if data["loaderVersion"].startswith("["):
                self.error_builder.println(
                    "- found forge-version indicator in mod from file {}, which is currently unsupported".format(
                        file
                    )
                )
                return

            version = data["loaderVersion"]

            if version.endswith("["):
                mc_version = 0  # todo: implement
            elif version.count("[") == version.count("]") == 0:
                mc_version = version.split("|")
            else:
                self.error_builder.println(
                    "[SOURCE][FATAL] can't decode version id '{}'".format(version)
                )
                return
        else:
            mc_version = None

        self.load_from_decoded_json(
            {"main files": [e["importable"] for e in data["main_files"]]}, file
        )

        for instance in self.located_mod_instances:
            instance.add_dependency(
                mcpython.common.mod.Mod.ModDependency("minecraft", mc_version)
            )

        for modname in data["dependencies"]:
            for dependency in data["dependencies"][modname]:
                name = dependency["modId"]
                if name != "forge":
                    self.mods[modname].add_dependency(name)
                    # todo: add version loader

    def add_to_add(self, instance: mcpython.common.mod.Mod.Mod):
        """
        Will add a mod-instance into the inner system
        :param instance: the mod instance to add
        Use only when really needed. The system is designed for beeing data-driven!
        """
        if not shared.event_handler.call_cancelable(
            "modloader:mod_registered", instance
        ):
            return

        self.mods[instance.name] = instance
        self.located_mods.append(instance)

        if instance.path is not None:
            instance.path = self.active_directory

        self.located_mod_instances.append(instance)

        return self

    def check_mod_duplicates(self):
        """
        Will check for mod duplicates
        :return an tuple of errors as string and collected mod-info's as dict
        todo: add config option for strategy: fail, load newest, load oldest, load all, load none
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
            for depend in mod.depend_info[0]:
                if not depend.arrival():
                    if shared.event_handler.call_cancelable(
                        "minecraft:modloader:missing_dependency", self, mod, depend
                    ):
                        self.error_builder.println(
                            "- Mod '{}' needs mod {} which is not provided".format(
                                mod.name, depend
                            )
                        )
                        errors = True

            for depend in mod.depend_info[2]:
                if depend.arrival():
                    if shared.event_handler.call_cancelable(
                        "minecraft:modloader:incompatible_mod", self, mod, depend
                    ):
                        self.error_builder.println(
                            "- Mod '{}' is incompatible with {} which is provided".format(
                                mod.name, depend
                            )
                        )
                        errors = True

            # todo: do we want two more events here?
            for depend in mod.depend_info[5]:
                if not depend.arrival():
                    del mod_info[mod.name]
                    del self.mods[mod.name]

            for depend in mod.depend_info[6]:
                if depend.arrival():
                    del mod_info[mod.name]
                    del self.mods[mod.name]

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
            logger.println(
                " -",
                "\n - ".join(
                    [instance.mod_string() for instance in self.mods.values()]
                ),
            )
            logger.println()

            self.error_builder.finish()
            sys.exit(-1)

        self.mod_loading_order = list(
            mcpython.util.math.topological_sort(
                [(key, mod_info[key]) for key in mod_info.keys()]
            )
        )

        self.error_builder.finish()
        logger.write_into_container(
            [
                " - {}".format(self.mods[name].mod_string())
                for name in self.mod_loading_order
            ]
        )

    def process(self):
        """
        Will process some loading tasks scheduled
        Used internally during mod loading state
        If on client, the renderer is also updated
        """
        if not mcpython.common.mod.ModLoadingStages.manager.order.is_active():
            return

        start = time.time()
        astate: mcpython.client.state.StateModLoading.StateModLoading = (
            shared.state_handler.active_state
        )
        astate.parts[0].progress_max = len(
            mcpython.common.mod.ModLoadingStages.manager.stages
        )
        astate.parts[1].progress_max = len(self.mods)

        while time.time() - start < 0.2:
            stage = mcpython.common.mod.ModLoadingStages.manager.get_stage()
            if stage is None:
                break

            if stage.call_one(astate):
                return

        # if shared.IS_CLIENT:
        self.update_pgb_text()

    def update_pgb_text(self):
        """
        Will update the text of the pgb's in mod loading
        """
        stage = mcpython.common.mod.ModLoadingStages.manager.get_stage()
        if stage is None:
            return

        astate: mcpython.client.state.StateModLoading.StateModLoading = (
            shared.state_handler.active_state
        )
        instance: mcpython.common.mod.Mod.Mod = self.mods[
            self.mod_loading_order[stage.active_mod_index]
        ]

        if (
            stage.active_event in instance.eventbus.event_subscriptions
            and len(instance.eventbus.event_subscriptions[stage.active_event]) > 0
        ):
            f, _, _, text = instance.eventbus.event_subscriptions[stage.active_event][0]
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
            self.active_loading_stage,
            len(mcpython.common.mod.ModLoadingStages.manager.stages),
        )


shared.mod_loader = ModLoader()
