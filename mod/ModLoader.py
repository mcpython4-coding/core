"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
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


class LoadingStage:
    def __init__(self, *eventnames):
        self.eventnames = eventnames
        self.running_event_names = eventnames
        self.progress = 0
        self.max_progress = 0

    def call_one(self, mod):
        if len(self.running_event_names) == 0: return False
        eventname = self.running_event_names[0]
        try:
            data = mod.eventbus.call_as_stack(eventname)
            self.progress += 1
            if self.running_event_names[0] in mod.eventbus.eventsubscribtions:
                self.max_progress = self.progress + len(mod.eventbus.eventsubscribtions[self.running_event_names[0]])
            return data[0][1] if len(data) > 0 else False
        except RuntimeError:
            self.running_event_names = self.running_event_names[1:]
            self.progress = 0
            return self.call_one(mod)


class LoadingStages:
    PREPARE = LoadingStage("stage:prepare")
    ADD_LOADING_STAGES = LoadingStage("stage:addition_of_stages")

    PREBUILD_TASKS = LoadingStage("stage:prebuild:addition")
    PREBUILD_DO = LoadingStage("stage:prebuild:do")

    EXTRA_RESOURCE_LOCATIONS = LoadingStage("stage:additional_resources")

    TAG_GROUPS = LoadingStage("stage:tag:group")  
    TAGS = LoadingStage("stage:tag:load")  
    BLOCK_BASES = LoadingStage("stage:block:base")  
    BLOCKS = LoadingStage("stage:block:load")  
    BLOCKS_OVERWRITE = LoadingStage("stage:block:overwrite")  
    ITEM_BASES = LoadingStage("stage:item:base")  
    ITEMS = LoadingStage("stage:item:load")  
    ITEMS_OVERWRITE = LoadingStage("stage:item:overwrite")  
    LANGUAGE = LoadingStage("stage:language")  
    RECIPE_GROUPS = LoadingStage("stage:recipe:groups")  
    RECIPES = LoadingStage("stage:recipes")
    RECIPE_BAKE = LoadingStage("stage:recipe:bake")
    INVENTORIES = LoadingStage("stage:inventories")  
    STATEPARTS = LoadingStage("stage:stateparts")  
    STATES = LoadingStage("stage:states")
    COMMAND_ENTRIES = LoadingStage("stage:command:entries")
    COMMANDS = LoadingStage("stage:commands")
    COMMAND_SELECTORS = LoadingStage("stage:command:selectors")
    BIOMES = LoadingStage("stage:worldgen:biomes")
    WORLDGENFEATURE = LoadingStage("stage:worldgen:feature")
    WORLDGENLAYER = LoadingStage("stage:worldgen:layer")
    WORLDGENMODE = LoadingStage("stage:worldgen:mode")
    DIMENSIONS = LoadingStage("stage:dimension")

    BLOCKSTATE_NOTATE = LoadingStage("stage:model:blockstate_search")
    BLOCKSTATE_CREATE = LoadingStage("stage:model:blockstate_create")
    MODEL_NOTATE = LoadingStage("stage:model:model_search")
    MODEL_CREATE = LoadingStage("stage:model:model_create")
    MODEL_BAKE_PREPARE = LoadingStage("stage:model:model_bake_prepare")
    MODEL_BAKE = LoadingStage("stage:model:model_bake")
    TEXTURE_ATLAS_BAKE = LoadingStage("stage:textureatlas:bake")

    POST = LoadingStage("stage:post")


LOADING_ORDER = [LoadingStages.PREPARE, LoadingStages.ADD_LOADING_STAGES, LoadingStages.PREBUILD_TASKS,
                 LoadingStages.PREBUILD_DO, LoadingStages.EXTRA_RESOURCE_LOCATIONS, LoadingStages.TAG_GROUPS,
                 LoadingStages.TAGS, LoadingStages.BLOCK_BASES, LoadingStages.BLOCKS, LoadingStages.BLOCKS_OVERWRITE,
                 LoadingStages.ITEM_BASES, LoadingStages.ITEMS, LoadingStages.ITEMS_OVERWRITE, LoadingStages.LANGUAGE,
                 LoadingStages.RECIPE_GROUPS, LoadingStages.RECIPES, LoadingStages.RECIPE_BAKE,
                 LoadingStages.INVENTORIES,
                 LoadingStages.COMMAND_ENTRIES, LoadingStages.COMMANDS, LoadingStages.COMMAND_SELECTORS,
                 LoadingStages.BIOMES, LoadingStages.WORLDGENFEATURE, LoadingStages.WORLDGENLAYER,
                 LoadingStages.WORLDGENMODE, LoadingStages.DIMENSIONS,
                 LoadingStages.STATEPARTS, LoadingStages.STATES, LoadingStages.MODEL_NOTATE, LoadingStages.MODEL_CREATE,
                 LoadingStages.BLOCKSTATE_NOTATE, LoadingStages.BLOCKSTATE_CREATE,
                 LoadingStages.MODEL_BAKE_PREPARE, LoadingStages.MODEL_BAKE,
                 LoadingStages.TEXTURE_ATLAS_BAKE,
                 LoadingStages.POST]


class ModLoader:
    def __init__(self):
        self.found_mods = []
        self.mods = {}
        self.modorder = []
        self.active_directory = None
        self.active_loading_stage = 0
        self.active_loading_mod = 0
        self.active_loading_mod_item_lenght = 0
        self.lasttime_mods = {}
        if os.path.exists(G.local+"/mods.json"):
            with open(G.local+"/mods.json") as f:
                self.lasttime_mods = json.load(f)

    def look_out(self):
        modlocations = []
        locs = [G.local+"/mods"]
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--addmoddir":
                locs.append(sys.argv[i+1])
                for _ in range(2): sys.argv.pop(i)
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
                    print("[WARNING] it was attempted to remove mod {} which was not found in file system".format(file))
                for _ in range(2): sys.argv.pop(i)
            else:
                i += 1
        for file in modlocations:
            if os.path.isfile(file):
                if zipfile.is_zipfile(file):  # compressed file
                    sys.path.append(file)
                    ResourceLocator.RESOURCE_LOCATIONS.append(ResourceLocator.ResourceZipFile(file))
                    self.active_directory = file
                    with zipfile.ZipFile(file) as f:
                        try:
                            with f.open("mod.json", mode="r") as sf:
                                data = json.load(sf)
                            if "main files" in data:
                                for location in data["main files"]:
                                    importlib.import_module(location)
                            else:
                                print("[ERROR] mod.json of '{}' does NOT contain 'main files'-attribute".format(file))
                        except FileNotFoundError:
                            print("[WARNING] can't locate mod.json file in mod at '{}'".format(file))
                elif file.endswith(".py"):  # python script file
                    self.active_directory = file
                    importlib.import_module("mods."+file.split(".")[0])
            elif os.path.isdir(file) and "__pycache__" not in file:  # source directory
                sys.path.append(file)
                ResourceLocator.RESOURCE_LOCATIONS.append(ResourceLocator.ResourceDirectory(file))
                self.active_directory = file
                if os.path.exists(file+"/mod.json"):
                    with open(file+"/mod.json") as sf:
                        data = json.load(sf)
                    if "main files" in data:
                        for location in data["main files"]:
                            importlib.import_module(location)
                    else:
                        print("[ERROR] mod.json of '{}' does NOT contain an 'main files'-attribute".format(file))
                else:
                    print("[WARNING] can't locate mod.json file for mod at '{}'".format(file))
        i = 0
        while i < len(sys.argv):
            element = sys.argv[i]
            if element == "--removemod":
                name = sys.argv[i+1]
                if name in self.mods:
                    del self.mods[name]
                else:
                    print("[WARNING] it was attempted to remove mod '{}' which was not registered".format(name))
                for _ in range(2): sys.argv.pop(i)
            else:
                i += 1
        print("found mods: {}".format(len(self.found_mods)))
        for modname in self.lasttime_mods.keys():
            if modname not in self.mods or self.mods[modname].version != self.lasttime_mods[modname]:
                # we have an mod which was previous loaded and not now or which was loaded before in another version
                G.prebuilding = True
        for modname in self.mods.keys():
            if modname not in self.lasttime_mods:
                # we have an mod which was loaded not previous but now
                G.prebuilding = True
        with open(G.local + "/mods.json", mode="w") as f:
            json.dump({modinst.name: modinst.version for modinst in self.mods.values()}, f)

    def add_to_add(self, mod):
        self.mods[mod.name] = mod
        self.found_mods.append(mod)
        mod.path = self.active_directory

    def sort_mods(self):
        modinfo = {}
        errors = []
        for mod in self.found_mods:
            if mod.name in modinfo:
                errors.append(
                    "-Mod '{}' has more than one version in the folder. Please load only every mod ONES".format(
                        mod.name))
                errors.append(" found in: {}".format(mod.path))
            else:
                modinfo[mod.name] = []
        for mod in self.found_mods:
            depends = mod.dependinfo[0][:]
            for depend in depends:
                if not depend.arrival():
                    errors.append("-Mod '{}' needs mod '{}' which is not provided".format(mod.name, depend))
            for depend in mod.dependinfo[2]:
                if depend.arrival():
                    errors.append("-Mod '{}' is incompatible with '{}'".format(mod.name, depend))
        for mod in self.found_mods:
            for depend in mod.dependinfo[4]:
                if depend.name in modinfo and depend.name not in modinfo[mod.name]:
                    modinfo[mod.name].append(depend.name)
            for depend in mod.dependinfo[3]:
                if depend.name in modinfo and mod.name not in modinfo[depend.name]:
                    modinfo[depend.name].append(mod.name)
        if len(errors) > 0:
            print("errors with mods:")
            print(" ", end="")
            print(*errors, sep="\n ")
            sys.exit(-1)
        self.modorder = list(util.math.topological_sort([(key, modinfo[key]) for key in modinfo.keys()]))
        print("mod loading order: ")
        print(" -", "\n - ".join(["{} ({})".format(name, self.mods[name].version) for name in self.modorder]))

    def process(self):
        start = time.time()
        state.StateModLoading.modloading.parts[1].progress_max = len(self.modorder)
        while time.time() - start < 0.2:
            modname = self.modorder[self.active_loading_mod]
            mod = self.mods[modname]
            stage: LoadingStage = LOADING_ORDER[self.active_loading_stage]
            result = stage.call_one(mod)
            state.StateModLoading.modloading.parts[2].progress = stage.progress + 1
            state.StateModLoading.modloading.parts[2].progress_max = stage.max_progress
            eventname = stage.running_event_names[0] if len(stage.running_event_names) > 0 else None
            state.StateModLoading.modloading.parts[2].text = mod.eventbus.eventsubscribtions[eventname][0][3] if \
                eventname in mod.eventbus.eventsubscribtions and len(
                    mod.eventbus.eventsubscribtions[eventname]) > 0 else "null"
            state.StateModLoading.modloading.parts[2].text += " ({}/{})".format(stage.progress, stage.max_progress)
            if result is False:  # finished with mod
                self.active_loading_mod += 1
                if self.active_loading_mod >= len(self.modorder):
                    self.active_loading_mod = 0
                    self.active_loading_stage += 1
                    if self.active_loading_stage >= len(LOADING_ORDER):
                        G.statehandler.switch_to("minecraft:blockitemgenerator")
                        return
                    state.StateModLoading.modloading.parts[0].progress = self.active_loading_stage + 1
                    state.StateModLoading.modloading.parts[0].progress_max = len(LOADING_ORDER)
                    state.StateModLoading.modloading.parts[0].text = ", ".join(list(stage.eventnames))
                    state.StateModLoading.modloading.parts[1].progress = self.active_loading_mod + 1
                    state.StateModLoading.modloading.parts[1].text = "{}: {} / {}".format(
                        self.modorder[self.active_loading_mod], self.active_loading_mod+1, len(self.modorder))
                else:
                    stage.running_event_names = LOADING_ORDER[self.active_loading_stage].eventnames
                    state.StateModLoading.modloading.parts[1].progress = self.active_loading_mod + 1
                    state.StateModLoading.modloading.parts[1].text = "{}: {} / {}".format(
                        self.modorder[self.active_loading_mod], self.active_loading_mod + 1, len(self.modorder))


G.modloader = ModLoader()


import mod.ModMcpython

