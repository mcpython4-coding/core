"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.event.EventHandler
from mcpython import shared as G, logger
import os
import mcpython.ResourceLoader
import zipfile
import sys
import json
import importlib
import time
import mcpython.client.state.StateModLoading
import mcpython.util.math
import mcpython.common.mod.Mod
import toml
import mcpython.common.config
import deprecation

# information for modders: this file contains every event called on the system
# you may NOT do any job beside registration to events outside of the loading events
# WARNING: violating this may cause problems
# WARNING: when your stage crashes, game may not
# WARNING: split up where possible to make showing progress bars easier
# WARNING: the order in which is loaded may change from version to version and from mod list to mod list

# For people who want to add their own loading stages: make sure to add them to LOADING_ORDER-list
# For people who want to tweak the order of loading: make sure to check if another mod has modified the same array
# For people who want to remove loading stages: make sure they really exists

# For people who are trying to resolve issues: make sure that you have a) subscribed to the event over the eventbus
#   of your mod [<modname>.eventbus] and have spelled the event correctly

# For people which bring their own assets with them: please, if you are not familiar with the whole asset loading
#   system, use the ResourceLocator.add_resources_by_modname-function to notate your loading to the right events

if not os.path.exists(G.home + "/mods"):
    os.makedirs(G.home + "/mods")


class LoadingStage:
    """
    class for any loading stage for the system
    """

    def __init__(self, name, *eventnames):
        """
        creates an new instance of LoadingStage
        :param name: the name of the stage
        :param eventnames: an list of events to call in this stage
        """
        self.name = name
        self.active_event_name = None
        self.active_mod_index = 0
        self.event_names = list(eventnames)
        self.running_event_names = eventnames
        self.progress = 0
        self.max_progress = 0

    @classmethod
    def finish(cls, astate):
        """
        will finish up the system
        :param astate: the state to use
        """
        G.mod_loader.active_loading_stage += 1
        if G.mod_loader.active_loading_stage >= len(LOADING_ORDER):
            logger.println(
                "[INFO] locking registries..."
            )  # ... and do similar stuff :-)
            G.event_handler.call("modloader:finished")

            G.state_handler.switch_to("minecraft:block_item_generator")
            G.mod_loader.finished = True
            return True
        astate.parts[0].progress += 1
        astate.parts[2].progress = 0
        new_stage = LOADING_ORDER[G.mod_loader.active_loading_stage]
        if (
            new_stage.event_names[0]
            in G.mod_loader.mods[
                G.mod_loader.mod_loading_order[0]
            ].eventbus.event_subscriptions
        ):
            astate.parts[2].progress_max = len(
                G.mod_loader.mods[
                    G.mod_loader.mod_loading_order[0]
                ].eventbus.event_subscriptions[new_stage.event_names[0]]
            )
        else:
            astate.parts[2].progress_max = 0

    def call_one(self, astate):
        """
        will call one event from the stack
        :param astate: the state to use
        """
        if self.active_mod_index >= len(G.mod_loader.mods):
            self.active_mod_index = 0
            if len(self.event_names) == 0:
                return self.finish(astate)
            self.active_event_name = self.event_names.pop(
                0
            )  # todo: is there an better way?
            mod_instance: mcpython.common.mod.Mod.Mod = G.mod_loader.mods[
                G.mod_loader.mod_loading_order[self.active_mod_index]
            ]
            if not G.event_handler.call_cancelable(
                "modloader:mod_entered_stage",
                self.name,
                self.active_event_name,
                mod_instance,
            ):
                self.active_mod_index += 1
                return
            self.max_progress = len(
                mod_instance.eventbus.event_subscriptions[self.active_event_name]
            )
            astate.parts[2].progress_max = self.max_progress
            astate.parts[2].progress = 0
            return
        if self.active_event_name is None:
            if len(self.event_names) == 0:
                return self.finish(astate)
            self.active_event_name = self.event_names.pop(0)
        modname = G.mod_loader.mod_loading_order[self.active_mod_index]
        mod_instance: mcpython.common.mod.Mod.Mod = G.mod_loader.mods[modname]
        try:
            mod_instance.eventbus.call_as_stack(self.active_event_name)
        except RuntimeError:
            self.active_mod_index += 1
            if self.active_mod_index >= len(G.mod_loader.mods):
                self.active_mod_index = 0
                if len(self.event_names) == 0:
                    return self.finish(astate)
                self.active_event_name = self.event_names.pop(0)
                mod_instance: mcpython.common.mod.Mod.Mod = G.mod_loader.mods[
                    G.mod_loader.mod_loading_order[self.active_mod_index]
                ]
                if self.active_event_name in mod_instance.eventbus.event_subscriptions:
                    self.max_progress = len(
                        mod_instance.eventbus.event_subscriptions[
                            self.active_event_name
                        ]
                    )
                else:
                    self.max_progress = 0
                astate.parts[2].progress_max = self.max_progress
                astate.parts[2].progress = 0
                return
            mod_instance: mcpython.common.mod.Mod.Mod = G.mod_loader.mods[
                G.mod_loader.mod_loading_order[self.active_mod_index]
            ]
            if self.active_event_name in mod_instance.eventbus.event_subscriptions:
                self.max_progress = len(
                    mod_instance.eventbus.event_subscriptions[self.active_event_name]
                )
            else:
                self.max_progress = 0
            astate.parts[2].progress_max = self.max_progress
            astate.parts[2].progress = 0
            return
        astate.parts[2].progress += 1  # todo: this is not good, can we optimize it?


class LoadingStages:
    """
    collection of all stages with their events
    """

    # used to do the magic stuff to set up your system
    PREPARE = LoadingStage("preparation phase", "stage:pre", "stage:mod:init")

    API_MANAGEMENT = LoadingStage(
        "working on api system",
        "stage:api:define",
        "stage:api:check",
        "stage:api:retrieve",
    )

    # this special phase is for adding new loading phases, if you want to
    ADD_LOADING_STAGES = LoadingStage(
        "loading stage register phase", "stage:addition_of_stages"
    )

    # if your mod has other resource locations...
    EXTRA_RESOURCE_LOCATIONS = LoadingStage(
        "resource addition", "stage:additional_resources"
    )

    # first: create ConfigFile objects, second: internally, third: do something with the data
    CONFIGS = LoadingStage(
        "loading mod config",
        "stage:mod:config:entry_loaders",
        "stage:mod:config:define",
        "stage:mod:config:load",
        "stage:mod:config:work",
    )

    # Stage collection for combined factories, last for building them
    COMBINED_FACTORIES = LoadingStage(
        "working on combined factories",
        "stage:combined_factory:blocks",
        "stage:combined_factory:build",
    )

    # blocks, items, inventories, ... all stuff to register
    BLOCKS = LoadingStage(
        "block loading phase",
        "stage:block:factory:prepare",
        "stage:block:factory_usage",
        "stage:block:factory:finish",
        "stage:block:load",
        "stage:block:overwrite",
        "stage:block:block_config",
    )
    ITEMS = LoadingStage(
        "item loading phase",
        "stage:item:factory:prepare",
        "stage:item:factory_usage",
        "stage:item:factory:finish",
        "stage:item:load",
        "stage:item:overwrite",
    )
    INVENTORIES = LoadingStage(
        "inventory loading phase",
        "stage:inventories:pre",
        "stage:inventories",
        "stage:inventories:post",
    )
    COMMANDS = LoadingStage(
        "command loading phase",
        "stage:command:entries",
        "stage:commands",
        "stage:command:selectors",
        "stage:command:gamerules",
    )
    ENTITIES = LoadingStage("entities", "stage:entities")

    # Optional stage for running the data generators. Only active in --data-gen mode
    DATA_GENERATION = LoadingStage(
        "generating special data",
        "special:datagen:configure",
        "special:datagen:generate",
    )

    # all the deserialization stuff, must be after data gen as data gen may want to inject some stuff
    LANGUAGE = LoadingStage("language file loading", "stage:language")
    TAGS = LoadingStage("tag loading phase", "stage:tag:group", "stage:tag:load")
    RECIPE = LoadingStage(
        "recipe loading phase",
        "stage:recipes",
        "stage:recipe:groups",
        "stage:recipe:bake",
    )
    LOOT_TABLES = LoadingStage(
        "loot tables",
        "stage:loottables:locate",
        "stage:loottables:functions",
        "stage:loottables:conditions",
        "stage:loottables:load",
    )

    # so, all stuff around block models & states
    MODEL_FACTORY = LoadingStage(
        "applying model factories",
        "stage:modelfactory:prepare",
        "stage:modefactory:use",
        "stage:modelfactory:bake",
        "stage:blockstatefactory:prepare",
        "stage:blockstatefactory:use",
        "stage:blockstatefactory:bake",
    )
    BLOCKSTATE = LoadingStage(
        "blockstate loading phase",
        "stage:blockstate:register_loaders",
        "stage:model:blockstate_search",
        "stage:model:blockstate_create",
        "stage:model:blockstate_bake",
    )
    BLOCK_MODEL = LoadingStage(
        "block loading phase",
        "stage:model:model_search",
        "stage:model:model_search:intern",
        "stage:model:model_create",
    )
    ITEM_MODEL = LoadingStage(
        "loading item models", "stage:model:item:search", "stage:model:item:bake"
    )
    BAKE = LoadingStage(
        "texture baking",
        "stage:model:model_bake_prepare",
        "stage:model:model_bake_lookup",
        "stage:model:model_bake:prepare",
        "stage:model:model_bake",
        "stage:textureatlas:bake",
        "stage:boxmodel:bake",
        "stage:block_boundingbox_get",
    )

    # now, the world gen, depends on results of registry system and data deserialization
    WORLDGEN = LoadingStage(
        "world generation loading phase",
        "stage:worldgen:biomes",
        "stage:worldgen:feature",
        "stage:worldgen:layer",
        "stage:worldgen:mode",
        "stage:dimension",
    )

    # How about storing stuff?
    FILE_INTERFACE = LoadingStage(
        "registration of data interfaces",
        "stage:serializer:parts",
        "stage:datafixer:general",
        "stage:datafixer:parts",
    )

    # Display-ables. Depends on most of above, nothing depends on
    STATES = LoadingStage(
        "state loading phase",
        "stage:stateparts",
        "stage:states",
        "stage:state_config:parser",
        "stage:state_config:generate",
        "stage:states:post",
    )

    POST = LoadingStage("finishing up", "stage:post", "stage:final")


# the order of stages todo: make serialized from config file
LOADING_ORDER: list = [
    LoadingStages.PREPARE,
    LoadingStages.API_MANAGEMENT,
    LoadingStages.ADD_LOADING_STAGES,
    LoadingStages.EXTRA_RESOURCE_LOCATIONS,
    LoadingStages.CONFIGS,
    LoadingStages.COMBINED_FACTORIES,
    LoadingStages.BLOCKS,
    LoadingStages.ITEMS,
    LoadingStages.INVENTORIES,
    LoadingStages.COMMANDS,
    LoadingStages.ENTITIES,
]

if G.data_gen:  # only do it in dev-environment
    LOADING_ORDER.append(LoadingStages.DATA_GENERATION)

    if G.data_gen_exit:
        LOADING_ORDER.append(LoadingStage("exit", "special:exit"))

LOADING_ORDER += [
    LoadingStages.LANGUAGE,
    LoadingStages.TAGS,
    LoadingStages.RECIPE,
    LoadingStages.LOOT_TABLES,
    LoadingStages.MODEL_FACTORY,
    LoadingStages.BLOCKSTATE,
    LoadingStages.ITEM_MODEL,
    LoadingStages.BLOCK_MODEL,
    LoadingStages.BAKE,
    LoadingStages.WORLDGEN,
    LoadingStages.FILE_INTERFACE,
    LoadingStages.STATES,
    LoadingStages.POST,
]


def insertAfter(to_insert: LoadingStage, after: LoadingStage) -> bool:
    if after not in LOADING_ORDER:
        return False
    LOADING_ORDER.insert(LOADING_ORDER.index(after) + 1, to_insert)
    return True


def insertBefore(to_insert: LoadingStage, before: LoadingStage) -> bool:
    if before not in LOADING_ORDER:
        return False
    LOADING_ORDER.insert(LOADING_ORDER.index(before), to_insert)
    return True


class ModLoaderAnnotation:
    def __init__(self, modname: str, event_name: str, info=None):
        """
        creates an new annotation
        :param modname: the name of the mod to annotate to
        :param event_name: the event name to subscribe to
        :param info: the info send to the event bus
        """
        self.modname = modname
        self.event_name = event_name
        self.info = info

    def __call__(self, function):
        """
        subscribes an function to the event
        :param function: the function to use
        :return: the function annotated
        """
        if self.modname not in G.mod_loader.mods:
            self.modname = "minecraft"
        G.mod_loader.mods[self.modname].eventbus.subscribe(
            self.event_name, function, info=self.info
        )
        return function


class ModLoader:
    """
    The mod loader class
    """

    def __init__(self):
        """
        creates an new modloader-instance
        """
        self.located_mods = []
        self.mods = {}
        self.mod_loading_order = []
        self.active_directory = None
        self.active_loading_stage = 0
        self.previous_mods = {}
        self.located_mod_instances = []
        if os.path.exists(G.build + "/mods.json"):
            with open(G.build + "/mods.json") as f:
                self.previous_mods = json.load(f)
        elif not G.invalidate_cache:
            logger.println(
                "[WARNING] can't locate mods.json in build-folder. This may be an error"
            )
        self.finished = False
        self.reload_stages = []
        mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
            "command:reload:end", self.execute_reload_stages
        )
        self.error_builder = logger.TableBuilder()

    def registerReloadAssignedLoadingStage(self, stage: str):
        """
        Will register an loading stage as one to executed on every reload
        :param stage: the event name of the stage
        """
        self.reload_stages.append(stage)

    def execute_reload_stages(self):
        for event_name in self.reload_stages:
            for i in range(len(self.mods)):
                instance = G.mod_loader.mods[G.mod_loader.mod_loading_order[i]]
                instance.eventbus.resetEventStack(event_name)
                instance.eventbus.call(event_name)

    def __call__(self, modname: str, event_name: str, info=None) -> ModLoaderAnnotation:
        """
        annotation to the event system
        :param modname: the mod name
        :param event_name: the event name
        :param info: the info
        :return: an ModLoaderAnnotation-instance for annotation
        """
        return ModLoaderAnnotation(modname, event_name, info)

    def __getitem__(self, item):
        return self.mods[item]

    def get_locations(self) -> list:
        """
        will return an list of mod locations found for loading
        todo: split up into smaller portions
        """
        modlocations = []
        locs = [G.home + "/mods"]
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--addmoddir":
                locs.append(sys.argv[i + 1])
                for _ in range(2):
                    sys.argv.pop(i)
                sys.path.append(locs[-1])
            elif element == "--addmodfile":
                modlocations.append(sys.argv[i + 1])
                for _ in range(2):
                    sys.argv.pop(i)
            else:
                i += 1
        for loc in locs:
            modlocations += [os.path.join(loc, x) for x in os.listdir(loc)]
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--removemodfile":
                file = sys.argv[i + 1]
                if file in modlocations:
                    modlocations.remove(file)
                else:
                    self.error_builder.println(
                        "-attempted to remove mod '{}' which is not found".format(file)
                    )
                for _ in range(2):
                    sys.argv.pop(i)
            else:
                i += 1

        G.event_handler.call("modloader:location_search", modlocations)

        for i, location in enumerate(modlocations):
            logger.ESCAPE[location.replace("\\", "/")] = "%MOD:{}%".format(i + 1)
        return modlocations

    def load_mod_jsons(self, locations: list):
        """
        will load the mod description files for the given locations and parse their content
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
                                self.load_mods_json(sf.read(), file)
                        except KeyError:
                            try:
                                with f.open("mod.toml", mode="r") as sf:
                                    self.load_mods_toml(sf.read(), file)
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
                    for modinst in self.located_mod_instances:
                        modinst.package = data
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
        will load all mods arrival
        """
        modlocations = self.get_locations()
        self.load_mod_jsons(modlocations)
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--removemod":
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
        will check for changes between versions
        """
        logger.println("found mod(s): {}".format(len(self.located_mods)))
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
                G.invalidate_cache = True
                G.data_gen = True
        for modname in self.mods.keys():
            if modname not in self.previous_mods:  # any new mods?
                # we have an mod which was loaded not previous but now
                G.invalidate_cache = True
                G.data_gen = True
                logger.println(
                    "rebuild mode due to mod change (addition) of {}".format(modname)
                )

    def write_mod_info(self):
        """
        writes the data for the mod table into the file
        """
        if not os.path.isdir(G.build):
            os.makedirs(G.build)
        with open(G.build + "/mods.json", mode="w") as f:
            m = {modinst.name: modinst.version for modinst in self.mods.values()}
            json.dump(m, f)

    def load_mods_json(self, data: str, file: str):
        """
        will parse the data to the correct system
        :param data: the data to load
        :param file: the file located under
        """
        self.load_from_decoded_json(json.loads(data), file)

    def load_from_decoded_json(self, data: dict, file: str):
        """
        will parse the decoded json-data to the correct system
        :param data: the data of the mod
        :param file: the file allocated (used for warning messages)
        """
        if "version" not in data:
            self.error_builder.println(
                "- version entry in '{}' is invalid due to version".format(file)
            )
        else:
            self.load_json(data, file)

    def load_json(self, data: dict, file: str):
        """
        load the stored json file
        :param data: the data to load
        :param file: the file to load, for debugging uses
        """
        if "version" not in data:
            self.error_builder.println(
                "- invalid mod.json file found without 'version'-entry in file {}".format(
                    file
                )
            )
            return
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
                    modinstance = mcpython.common.mod.Mod.Mod(modname, version)
                    if "depends" in entry:
                        for depend in entry["depends"]:
                            t = None if "type" not in depend else depend["type"]
                            if t is None or t == "depend":
                                modinstance.add_dependency(self.cast_dependency(depend))
                            elif t == "depend_not_load_order":
                                modinstance.add_not_load_dependency(
                                    self.cast_dependency(depend)
                                )
                            elif t == "not_compatible":
                                modinstance.add_not_compatible(
                                    self.cast_dependency(depend)
                                )
                            elif t == "load_before":
                                modinstance.add_load_before_if_arrival(
                                    self.cast_dependency(depend)
                                )
                            elif t == "load_after":
                                modinstance.add_load_after_if_arrival(
                                    self.cast_dependency(depend)
                                )
                            elif t == "only_if":
                                modinstance.add_load_only_when_arrival(
                                    self.cast_dependency(depend)
                                )
                            elif t == "only_if_not":
                                modinstance.add_load_only_when_not_arrival(
                                    self.cast_dependency(depend)
                                )
                    if "load_resources" in entry and entry["load_resources"]:
                        modinstance.add_load_default_resources()
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

    def load_mods_toml(self, data: str, file):
        """
        will load an toml-data-object
        :param data: the toml-representation
        :param file: the file for debugging reasons
        """
        data = toml.loads(data)
        if "modLoader" in data:
            if data["modLoader"] == "javafml":
                self.error_builder.println(
                    "- found java mod. As an mod-author, please upgrade to python as javafml"
                )
                return
        if "loaderVersion" in data:
            if data["loaderVersion"].startswith("["):
                self.error_builder.println("- found forge-version indicator")
                return
            version = data["loaderVersion"]
            if version.endswith("["):
                mc_version = mcpython.common.config.VERSION_ORDER[
                    mcpython.common.config.VERSION_ORDER.index(version[:-1]) :
                ]
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
        for modinstance in self.located_mod_instances:
            modinstance.add_dependency(
                mcpython.common.mod.Mod.ModDependency("minecraft", mc_version)
            )
        for modname in data["dependencies"]:
            for dependency in data["dependencies"][modname]:
                dependname = dependency["modId"]
                if dependname != "forge":
                    self.mods[modname].add_dependency(dependname)
                    # todo: add version loader

    def add_to_add(self, instance: mcpython.common.mod.Mod.Mod):
        """
        will add an mod-instance into the inner system
        :param instance: the mod instance to add
        """
        if not G.event_handler.call_cancelable("modloader:mod_registered", instance):
            return
        self.mods[instance.name] = instance
        self.located_mods.append(instance)
        instance.path = self.active_directory
        self.located_mod_instances.append(instance)

    def check_mod_duplicates(self):
        """
        will check for mod duplicates
        :return an tuple of errors as string and collected mod-info's as dict
        todo: add config option for strategy: fail, load newest, load oldest, load all
        """
        errors = False
        modinfo = {}
        for mod in self.located_mods:
            if mod.name in modinfo:
                self.error_builder.println(
                    " -Mod '{}' found in {} has more than one version in the folder. Please load only every mod ONES".format(
                        mod.name,
                        mod.path,
                    )
                )
                errors = True
            else:
                modinfo[mod.name] = []
        return errors, modinfo

    def check_dependency_errors(self, errors: bool, modinfo: dict):
        """
        will iterate through
        :param errors: the error list
        :param modinfo: the mod info dict
        :return: errors and modinfo-tuple
        """
        for mod in self.located_mods:
            for depend in mod.dependinfo[0]:
                if not depend.arrival():
                    self.error_builder.println(
                        "- Mod '{}' needs mod {} which is not provided".format(
                            mod.name, depend
                        )
                    )
            for depend in mod.dependinfo[2]:
                if depend.arrival():
                    self.error_builder.println(
                        "- Mod '{}' is incompatible with {} which is provided".format(
                            mod.name, depend
                        )
                    )
            for depend in mod.dependinfo[5]:
                if not depend.arrival():
                    del modinfo[mod.name]
                    del self.mods[mod.name]
            for depend in mod.dependinfo[6]:
                if depend.arrival():
                    del modinfo[mod.name]
                    del self.mods[mod.name]
        return errors, modinfo

    def sort_mods(self):
        """
        will create the modorder-list by sorting after dependencies
        """
        errors, modinfo = self.check_dependency_errors(*self.check_mod_duplicates())
        for mod in self.located_mods:
            for depend in mod.dependinfo[4]:
                if mod.name in modinfo and depend.name not in modinfo[mod.name]:
                    modinfo[mod.name].append(depend.name)
            for depend in mod.dependinfo[3]:
                if depend.name in modinfo and mod.name not in modinfo[depend.name]:
                    modinfo[depend.name].append(mod.name)
        if errors:
            logger.println("found mods: ")
            logger.println(
                " -",
                "\n - ".join(
                    [modinstance.mod_string() for modinstance in self.mods.values()]
                ),
            )
            logger.println()

            self.error_builder.finish()
            sys.exit(-1)
        self.mod_loading_order = list(
            mcpython.util.math.topological_sort(
                [(key, modinfo[key]) for key in modinfo.keys()]
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
        will process some loading tasks
        """
        if self.active_loading_stage >= len(LOADING_ORDER):
            return
        start = time.time()
        astate: mcpython.client.state.StateModLoading.StateModLoading = (
            G.state_handler.active_state
        )
        astate.parts[0].progress_max = len(LOADING_ORDER)
        astate.parts[1].progress_max = len(self.mods)
        while time.time() - start < 0.2:
            stage = LOADING_ORDER[self.active_loading_stage]
            if stage.call_one(astate):
                return
        self.update_pgb_text()

    def update_pgb_text(self):
        """
        will update the text of the pgb's in mod loading
        """
        stage = LOADING_ORDER[self.active_loading_stage]
        astate: mcpython.client.state.StateModLoading.StateModLoading = (
            G.state_handler.active_state
        )
        modinst: mcpython.common.mod.Mod.Mod = self.mods[
            self.mod_loading_order[stage.active_mod_index]
        ]
        if (
            stage.active_event_name in modinst.eventbus.event_subscriptions
            and len(modinst.eventbus.event_subscriptions[stage.active_event_name]) > 0
        ):
            f, _, _, text = modinst.eventbus.event_subscriptions[
                stage.active_event_name
            ][0]
        else:
            f, text = None, ""
        astate.parts[2].text = text if text is not None else "function {}".format(f)
        astate.parts[1].text = "{} ({}/{})".format(
            modinst.name, stage.active_mod_index + 1, len(self.mods)
        )
        astate.parts[1].progress = stage.active_mod_index + 1
        index = (
            stage.running_event_names.index(stage.active_event_name) + 1
            if stage.active_event_name in stage.running_event_names
            else 0
        )
        astate.parts[0].text = "{} ({}/{}) in {} ({}/{})".format(
            stage.active_event_name,
            index,
            len(stage.running_event_names),
            stage.name,
            self.active_loading_stage + 1,
            len(LOADING_ORDER),
        )


G.mod_loader = ModLoader()
