"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import event.EventHandler
import globals as G
import os
import ResourceLocator
import zipfile
import sys
import json
import importlib
import time
import state.StateModLoading
import util.math
import mod.Mod
import enum
import toml
import config
import logger
from util.enums import LoadingStageStatus


if not os.path.exists(G.local+"/mods"):
    os.makedirs(G.local+"/mods")


class LoadingStage:
    def __init__(self, name, *eventnames):
        self.name = name
        self.active_event_name = None
        self.active_mod_index = 0
        self.eventnames = list(eventnames)
        self.running_event_names = eventnames
        self.progress = 0
        self.max_progress = 0

    def call_one(self) -> LoadingStageStatus:
        if self.active_mod_index >= len(G.modloader.mods):
            self.active_mod_index = 0
            if len(self.eventnames) == 0: return LoadingStageStatus.FINISHED
            self.active_event_name = self.eventnames.pop(0)
            modinst: mod.Mod.Mod = G.modloader.mods[G.modloader.modorder[self.active_mod_index]]
            self.max_progress = len(modinst.eventbus.event_subscriptions[self.active_event_name])
            return LoadingStageStatus.EVENT_CHANGED
        if self.active_event_name is None:
            if len(self.eventnames) == 0: return LoadingStageStatus.FINISHED
            self.active_event_name = self.eventnames.pop(0)
        modname = G.modloader.modorder[self.active_mod_index]
        modinst: mod.Mod.Mod = G.modloader.mods[modname]
        try:
            modinst.eventbus.call_as_stack(self.active_event_name)
        except RuntimeError:
            self.active_mod_index += 1
            if self.active_mod_index >= len(G.modloader.mods):
                self.active_mod_index = 0
                if len(self.eventnames) == 0: return LoadingStageStatus.FINISHED
                self.active_event_name = self.eventnames.pop(0)
                modinst: mod.Mod.Mod = G.modloader.mods[G.modloader.modorder[self.active_mod_index]]
                if self.active_event_name in modinst.eventbus.event_subscriptions:
                    self.max_progress = len(modinst.eventbus.event_subscriptions[self.active_event_name])
                else:
                    self.max_progress = 0
                return LoadingStageStatus.EVENT_CHANGED
            modinst: mod.Mod.Mod = G.modloader.mods[G.modloader.modorder[self.active_mod_index]]
            if self.active_event_name in modinst.eventbus.event_subscriptions:
                self.max_progress = len(modinst.eventbus.event_subscriptions[self.active_event_name])
            else:
                self.max_progress = 0
            return LoadingStageStatus.MOD_CHANGED
        return LoadingStageStatus.WORKING


class LoadingStages:
    PREPARE = LoadingStage("preparation phase", "stage:prepare")
    ADD_LOADING_STAGES = LoadingStage("loading stage register phase", "stage:addition_of_stages")

    PREBUILD = LoadingStage("prebuilding", "stage:prebuild:addition", "stage:prebuild:do")

    EXTRA_RESOURCE_LOCATIONS = LoadingStage("resource addition", "stage:additional_resources")

    TAGS = LoadingStage("tag loading phase", "stage:tag:group", "stage:tag:load")
    BLOCKS = LoadingStage("block loading phase", "stage:block:base", "stage:block:load", "stage:block:overwrite",
                          "stage:block:block_config")
    ITEMS = LoadingStage("item loading phase", "stage:item:base", "stage:item:load", "stage:item:overwrite")
    LANGUAGE = LoadingStage("language file loading", "stage:language")
    RECIPE = LoadingStage("recipe loading phase", "stage:recipes", "stage:recipe:groups", "stage:recipe:bake")
    INVENTORIES = LoadingStage("inventory loading phase", "stage:inventories")
    STATES = LoadingStage("state loading phase", "stage:stateparts", "stage:states")
    COMMANDS = LoadingStage("command loading phase", "stage:command:entries", "stage:commands",
                            "stage:command:selectors")
    WORLDGEN = LoadingStage("world generation loading phase", "stage:worldgen:biomes", "stage:worldgen:feature",
                            "stage:worldgen:layer", "stage:worldgen:mode", "stage:dimension")

    BLOCKSTATE = LoadingStage("blockstate loading phase", "stage:model:blockstate_search",
                              "stage:model:blockstate_create")
    BLOCK_MODEL = LoadingStage("block loading phase", "stage:model:model_search", "stage:model:model_create")

    BAKE = LoadingStage("texture baking", "stage:model:model_bake_prepare", "stage:model:model_bake_lookup",
                        "stage:model:model_bake:prepare", "stage:model:model_bake", "stage:textureatlas:bake")

    POST = LoadingStage("finishing up", "stage:post")


LOADING_ORDER = [LoadingStages.PREPARE, LoadingStages.ADD_LOADING_STAGES, LoadingStages.PREBUILD,
                 LoadingStages.EXTRA_RESOURCE_LOCATIONS,
                 LoadingStages.TAGS, LoadingStages.BLOCKS, LoadingStages.ITEMS, LoadingStages.LANGUAGE,
                 LoadingStages.RECIPE, LoadingStages.INVENTORIES, LoadingStages.COMMANDS,
                 LoadingStages.WORLDGEN, LoadingStages.STATES, LoadingStages.BLOCK_MODEL,
                 LoadingStages.BLOCKSTATE, LoadingStages.BAKE, LoadingStages.POST]


class ModLoader:
    def __init__(self):
        self.found_mods = []
        self.mods = {}
        self.modorder = []
        self.active_directory = None
        self.active_loading_stage = 0
        self.lasttime_mods = {}
        self.found_mod_instances = []
        if os.path.exists(G.local+"/build/mods.json"):
            with open(G.local+"/build/mods.json") as f:
                self.lasttime_mods = json.load(f)
        elif not G.prebuilding:
            logger.println("[WARNING] can't locate mods.json in build-folder. This may be an error")

    def look_out(self):
        event.EventHandler.PUBLIC_EVENT_BUS.subscribe("prebuilding:finished", self.write_mod_info)
        modlocations = []
        locs = [G.local+"/mods"]
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--addmoddir":
                locs.append(sys.argv[i+1])
                for _ in range(2): sys.argv.pop(i)
                sys.path.append(locs[-1])
            elif element == "--addmodfile":
                modlocations.append(sys.argv[i+1])
                for _ in range(2): sys.argv.pop(i)
            else:
                i += 1
        for loc in locs:
            modlocations += [os.path.join(loc, x) for x in os.listdir(loc)]
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--removemodfile":
                file = sys.argv[i+1]
                if file in modlocations:
                    modlocations.remove(file)
                else:
                    logger.println("[WARNING] it was attempted to remove mod {} which was not found in file system".format(file))
                for _ in range(2): sys.argv.pop(i)
            else:
                i += 1
        for file in modlocations:
            self.found_mod_instances.clear()
            if os.path.isfile(file):
                if zipfile.is_zipfile(file):  # compressed file
                    sys.path.append(file)
                    ResourceLocator.RESOURCE_LOCATIONS.insert(0, ResourceLocator.ResourceZipFile(file))
                    self.active_directory = file
                    with zipfile.ZipFile(file) as f:
                        try:
                            with f.open("mod.json", mode="r") as sf: self.load_mods_json(sf.read(), file)
                        except KeyError:
                            try:
                                with f.open("mod.toml", mode="r") as sf: self.load_mods_toml(sf.read(), file)
                            except KeyError:
                                logger.println("[WARNING] can't locate mod.json file in mod at '{}'".format(file))
                elif file.endswith(".py"):  # python script file
                    self.active_directory = file
                    try:
                        data = importlib.import_module("mods."+file.split("/")[-1].split("\\")[-1].split(".")[0])
                    except ModuleNotFoundError:
                        data = importlib.import_module(file.split("/")[-1].split("\\")[-1].split(".")[0])
                    for modinst in self.found_mod_instances: modinst.package = data
            elif os.path.isdir(file) and "__pycache__" not in file:  # source directory
                sys.path.append(file)
                ResourceLocator.RESOURCE_LOCATIONS.insert(0, ResourceLocator.ResourceDirectory(file))
                self.active_directory = file
                if os.path.exists(file+"/mod.json"):
                    with open(file+"/mod.json") as sf: self.load_mods_json(sf.read(), file+"/mod.json")
                elif os.path.exists(file+"/mods.toml"):
                    with open(file+"/mods.toml") as sf: self.load_mods_toml(sf.read(), file+"/mods.toml")
                else:
                    logger.println("[WARNING] can't locate mod.json file for mod at '{}'".format(file))
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--removemod":
                name = sys.argv[i+1]
                if name in self.mods:
                    del self.mods[name]
                else:
                    logger.println("[WARNING] it was attempted to remove mod '{}' which was not registered".format(name))
                for _ in range(2): sys.argv.pop(i)
            else:
                i += 1
        logger.println("found mods: {}".format(len(self.found_mods)))
        for modname in self.lasttime_mods.keys():
            if modname not in self.mods or self.mods[modname].version != self.lasttime_mods[modname]:
                # we have an mod which was previous loaded and not now or which was loaded before in another version
                G.prebuilding = True
        for modname in self.mods.keys():
            if modname not in self.lasttime_mods:  # any new mods?
                # we have an mod which was loaded not previous but now
                G.prebuilding = True

    def write_mod_info(self):
        with open(G.local + "/build/mods.json", mode="w") as f:
            m = {modinst.name: modinst.version for modinst in self.mods.values()}
            json.dump(m, f)

    def load_mods_json(self, data: str, file: str):
        self.load_from_decoded_json(json.loads(data), file)

    @staticmethod
    def load_from_decoded_json(data: dict, file: str):
        if "main files" in data:
            files = data["main files"]
            for location in (files if type(files) == list else [files]):
                importlib.import_module(location)
        else:
            logger.println("[ERROR] mod.json of '{}' does NOT contain an 'main files'-attribute".format(file))

    def load_mods_toml(self, data: str, file):
        data = toml.loads(data)
        if 'modLoader' in data:
            if data['modLoader'] == "javafml":
                logger.println("[SOURCE][FATAL] found java mod. As an mod-author, please upgrade to python as javafml")
                sys.exit(-1)
        if 'loaderVersion' in data:
            if data['loaderVersion'].startswith("["):
                logger.println("[SOURCE][FATAL] found forge-version indicator")
                sys.exit(-1)
            version = data["loaderVersion"]
            if version.endswith("["):
                mc_version = config.VERSION_ORDER[config.VERSION_ORDER.index(version[:-1]):]
            elif version.count("[") == version.count("]") == 0:
                mc_version = version.split("|")
            else:
                logger.println("[SOURCE][FATAL] can't decode version id '{}'".format(version))
                sys.exit(-1)
        else:
            mc_version = None
        self.load_from_decoded_json({"main files": [e["importable"] for e in data['main_files']]}, file)
        for modinstance in self.found_mod_instances:
            modinstance.add_dependency(mod.Mod.ModDependency("minecraft", mc_version))
        for modname in data['dependencies']:
            for dependency in data['dependencies'][modname]:
                dependname = dependency["modId"]
                if dependname != "forge":
                    self.mods[modname].add_dependency(dependname)
                    # todo: add version loader

    def add_to_add(self, mod):
        G.eventhandler.call("modloader:mod_found", mod)
        self.mods[mod.name] = mod
        self.found_mods.append(mod)
        mod.path = self.active_directory
        self.found_mod_instances.append(mod)

    def sort_mods(self):
        modinfo = {}
        errors = []
        for mod in self.found_mods:
            if mod.name in modinfo:
                errors.append(
                    " -Mod '{}' has more than one version in the folder. Please load only every mod ONES".format(
                        mod.name))
                errors.append(" found in: {}".format(mod.path))
            else:
                modinfo[mod.name] = []
        for mod in self.found_mods:
            depends = mod.dependinfo[0][:]
            for depend in depends:
                if not depend.arrival():
                    errors.append("- Mod '{}' needs mod '{}' which is not provided".format(mod.name, depend))
            for depend in mod.dependinfo[2]:
                if depend.arrival():
                    errors.append("- Mod '{}' is incompatible with '{}'".format(mod.name, depend))
        for mod in self.found_mods:
            for depend in mod.dependinfo[4]:
                if depend.name in modinfo and depend.name not in modinfo[mod.name]:
                    modinfo[mod.name].append(depend.name)
            for depend in mod.dependinfo[3]:
                if depend.name in modinfo and mod.name not in modinfo[depend.name]:
                    modinfo[depend.name].append(mod.name)
        if len(errors) > 0:
            logger.println("errors with mods:")
            logger.println(" ", end="")
            logger.println(*errors, sep="\n ")
            sys.exit(-1)
        self.modorder = list(util.math.topological_sort([(key, modinfo[key]) for key in modinfo.keys()]))
        logger.println("mod loading order: ")
        logger.println(" -", "\n - ".join(["{} ({})".format(name, self.mods[name].version) for name in self.modorder]))

    def process(self):
        start = time.time()
        astate: state.StateModLoading.StateModLoading = G.statehandler.active_state
        astate.parts[0].progress_max = len(LOADING_ORDER)
        astate.parts[1].progress_max = len(self.mods)
        while time.time() - start < 0.2:
            stage = LOADING_ORDER[self.active_loading_stage]
            status = stage.call_one()
            if status == LoadingStageStatus.WORKING:
                astate.parts[2].progress += 1
                self.update_pgb_text()
            elif status == LoadingStageStatus.MOD_CHANGED:
                astate.parts[2].progress_max = stage.max_progress
                astate.parts[2].progress = 0
                self.update_pgb_text()
            elif status == LoadingStageStatus.EVENT_CHANGED:
                self.update_pgb_text()
                astate.parts[2].progress_max = stage.max_progress
                astate.parts[2].progress = 0
            elif status == LoadingStageStatus.FINISHED:
                self.active_loading_stage += 1
                if self.active_loading_stage >= len(LOADING_ORDER):
                    G.statehandler.switch_to("minecraft:blockitemgenerator")
                    return
                astate.parts[0].progress += 1
                astate.parts[2].progress = 0
                new_stage = LOADING_ORDER[self.active_loading_stage]
                if new_stage.eventnames[0] in self.mods[self.modorder[0]].eventbus.event_subscriptions:
                    astate.parts[2].progress_max = len(self.mods[self.modorder[0]].eventbus.event_subscriptions[
                                                           new_stage.eventnames[0]])
                else:
                    astate.parts[2].progress_max = 0
                self.update_pgb_text()

    def update_pgb_text(self):
        stage = LOADING_ORDER[self.active_loading_stage]
        astate: state.StateModLoading.StateModLoading = G.statehandler.active_state
        modinst: mod.Mod.Mod = self.mods[self.modorder[stage.active_mod_index]]
        if stage.active_event_name in modinst.eventbus.event_subscriptions and \
                len(modinst.eventbus.event_subscriptions[stage.active_event_name]) > 0:
            f, _, _, text = modinst.eventbus.event_subscriptions[stage.active_event_name][0]
        else:
            f, text = None, ""
        astate.parts[2].text = text if text is not None else "function {}".format(f)
        astate.parts[1].text = "{} ({}/{})".format(modinst.name, stage.active_mod_index+1, len(self.mods))
        astate.parts[1].progress = stage.active_mod_index + 1
        index = stage.running_event_names.index(stage.active_event_name)+1 if stage.active_event_name in \
                                                                              stage.running_event_names else 0
        astate.parts[0].text = "{} ({}/{}) in {} ({}/{})".format(
            stage.active_event_name, index, len(stage.running_event_names), stage.name, self.active_loading_stage+1,
            len(LOADING_ORDER))


G.modloader = ModLoader()


import mod.ModMcpython

