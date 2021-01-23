"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import importlib
import json
import os
import sys
import time
import typing
import zipfile

import toml

import mcpython.client.state.StateModLoading
import mcpython.common.config
import mcpython.common.event.EventHandler
import mcpython.common.mod.Mod
import mcpython.common.mod.ModLoadingPipe
import mcpython.ResourceLoader
import mcpython.util.math
from mcpython import logger
from mcpython import shared


class ModLoader:
    """
    The mod loader class
    """

    def __init__(self):
        """
        Creates an new mod-loader-instance
        WARNING: only ONE instance should be present.
        When creating a second instance, you should know what you are doing!
        """
        self.located_mods: typing.List[mcpython.common.mod.Mod.Mod] = []
        self.mods: typing.Dict[str, mcpython.common.mod.Mod.Mod] = {}
        self.mod_loading_order: typing.List[str] = []
        self.active_directory: typing.Optional[str] = None
        self.active_loading_stage: int = 0
        self.previous_mods = {}
        self.located_mod_instances = []

        if os.path.exists(shared.build + "/mods.json"):
            with open(shared.build + "/mods.json") as f:
                self.previous_mods = json.load(f)

        self.finished = False
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

    def execute_reload_stages(self):
        # todo: remove -> resource pipe
        for event_name in self.reload_stages:
            for i in range(len(self.mods)):
                instance = shared.mod_loader.mods[
                    shared.mod_loader.mod_loading_order[i]
                ]
                instance.eventbus.resetEventStack(event_name)
                instance.eventbus.call(event_name)

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

    def __contains__(self, item):
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
                        "-attempted to remove mod '{}' which is not found".format(file)
                    )
                for _ in range(2):
                    sys.argv.pop(i)
            else:
                i += 1

        shared.event_handler.call("modloader:location_search", locations)

        for i, location in enumerate(locations):
            logger.ESCAPE[location.replace("\\", "/")] = "%MOD:{}%".format(i + 1)

        return locations

    def load_mod_json_from_locations(self, locations: typing.List[str]):
        """
        Will load the mod description files for the given locations and parse their content
        :param locations: the locations found
        """
        for file in locations:
            self.located_mod_instances.clear()

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
                        self.load_mods_json(sf.read(), file + "/mod.json")
                elif os.path.exists(file + "/mods.toml"):
                    with open(file + "/mods.toml") as sf:
                        self.load_mods_toml(sf.read(), file + "/mods.toml")
                else:
                    self.error_builder.println(
                        "- could not locate mod.json file for mod at '{}'".format(file)
                    )

    def look_out(self):
        """
        Will load all mods arrival
        """
        locations = self.get_locations()
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

        self.check_for_update()

    def check_for_update(self):
        """
        Will check for changes between versions
        """
        logger.println(
            "found mod{}: {}".format(
                "s" if len(self.located_mods) > 1 else "", len(self.located_mods)
            )
        )

        for modname in self.previous_mods.keys():
            if modname not in self.mods or self.mods[modname].version != tuple(
                self.previous_mods[modname]
            ):
                # we have an mod which was previous loaded and not now or which was loaded before in another version
                logger.println(
                    "rebuild mode due to mod change (remove / version change) of {}".format(
                        modname
                    )
                )
                shared.invalidate_cache = True
                shared.data_gen = True

        for modname in self.mods.keys():
            if modname not in self.previous_mods:  # any new mods?
                # we have an mod which was loaded not previous but now
                shared.invalidate_cache = True
                shared.data_gen = True
                logger.println(
                    "rebuild mode due to mod change (addition) of {}".format(modname)
                )

    def write_mod_info(self):
        """
        Writes the data for the mod table into the file
        """
        if not os.path.isdir(shared.build):
            os.makedirs(shared.build)
        with open(shared.build + "/mods.json", mode="w") as f:
            m = {instance.name: instance.version for instance in self.mods.values()}
            json.dump(m, f)

    def load_mods_json(self, data: str, file: str):
        """
        Will parse the data to the correct system
        :param data: the data to load
        :param file: the file located under
        """
        self.load_from_decoded_json(json.loads(data), file)

    def load_from_decoded_json(self, data: dict, file: str):
        """
        Will parse the decoded json-data to the correct system
        :param data: the data of the mod
        :param file: the file allocated (used for warning messages)
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
                else:
                    raise IOError("invalid loader '{}'".format(loader))

    @classmethod
    def cast_dependency(cls, depend: dict):
        """
        will cast an dict-structure to the depend
        :param depend: the depend dict
        :return: the parsed mod.Mod.ModDependency-object
        """
        c = {}
        if "version" in depend:
            c["version_min"] = depend["version"]
        if "upper_version" in depend:
            c["version_max"] = depend["upper_version"]
        if "versions" in depend:
            c["versions"] = depend["versions"]

        return mcpython.common.mod.Mod.ModDependency(depend["name"], **c)

    def load_mods_toml(self, data: str, file: str):
        """
        will load an toml-data-object
        :param data: the toml-representation
        :param file: the file for debugging reasons
        """
        data = toml.loads(data)
        if "modLoader" in data:
            if data["modLoader"] == "javafml":
                self.error_builder.println(
                    "- found java mod in file {}. As an mod-author, please upgrade to python as javafml or wait for us to write an JVM in python [WIP]".format(
                        file
                    )
                )
                return

        if "loaderVersion" in data:
            if data["loaderVersion"].startswith("["):
                self.error_builder.println("- found forge-version indicator")
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
        Will add an mod-instance into the inner system
        :param instance: the mod instance to add
        """
        if not shared.event_handler.call_cancelable(
            "modloader:mod_registered", instance
        ):
            return

        self.mods[instance.name] = instance
        self.located_mods.append(instance)
        instance.path = self.active_directory
        self.located_mod_instances.append(instance)

    def check_mod_duplicates(self):
        """
        Will check for mod duplicates
        :return an tuple of errors as string and collected mod-info's as dict
        todo: add config option for strategy: fail, load newest, load oldest, load all
        """
        errors = False
        mod_info = {}

        for mod in self.located_mods:
            if mod.name in mod_info:
                self.error_builder.println(
                    " -Mod '{}' found in {} has more than one version in the folder. Please load only every mod ONES".format(
                        mod.name,
                        mod.path,
                    )
                )
                errors = True
            else:
                mod_info[mod.name] = []

        return errors, mod_info

    def check_dependency_errors(self, errors: bool, mod_info: dict):
        """
        Will iterate through
        :param errors: the error list
        :param mod_info: the mod info dict
        :return: errors and mod-info-tuple
        """
        for mod in self.located_mods:
            for depend in mod.depend_info[0]:
                if not depend.arrival():
                    self.error_builder.println(
                        "- Mod '{}' needs mod {} which is not provided".format(
                            mod.name, depend
                        )
                    )

            for depend in mod.depend_info[2]:
                if depend.arrival():
                    self.error_builder.println(
                        "- Mod '{}' is incompatible with {} which is provided".format(
                            mod.name, depend
                        )
                    )

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
        """
        if not mcpython.common.mod.ModLoadingPipe.manager.order.is_active():
            return

        start = time.time()
        astate: mcpython.client.state.StateModLoading.StateModLoading = (
            shared.state_handler.active_state
        )
        astate.parts[0].progress_max = len(
            mcpython.common.mod.ModLoadingPipe.manager.stages
        )
        astate.parts[1].progress_max = len(self.mods)

        while time.time() - start < 0.2:
            stage = mcpython.common.mod.ModLoadingPipe.manager.get_stage()
            if stage is None:
                break
            if stage.call_one(astate):
                return

        self.update_pgb_text()

    def update_pgb_text(self):
        """
        Will update the text of the pgb's in mod loading
        """
        stage = mcpython.common.mod.ModLoadingPipe.manager.get_stage()
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
            len(mcpython.common.mod.ModLoadingPipe.manager.stages),
        )


shared.mod_loader = ModLoader()
