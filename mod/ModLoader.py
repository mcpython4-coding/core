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
import toposort
import time
import state.StateModLoading


class LoadingStage:
    def __init__(self, *eventnames):
        self.eventnames = eventnames

    def call_one(self, mod):
        if len(self.eventnames) == 0: return False
        eventname = self.eventnames[0]
        try:
            data = mod.eventbus.call_as_stack(eventname)
            return data[0][1] if len(data) > 0 else False
        except RuntimeError:
            self.eventnames = self.eventnames[1:]
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
    INVENTORIES = LoadingStage("stage:inventories")  
    STATEPARTS = LoadingStage("stage:stateparts")  
    STATES = LoadingStage("stage:states")

    BLOCKSTATE_NOTATE = LoadingStage("stage:model:blockstate_search")
    MODEL_NOTATE = LoadingStage("stage:model:model_search")
    MODEL_BAKE = LoadingStage("stage:model:model_bake")
    TEXTURE_ATLAS_BAKE = LoadingStage("stage:textureatlas:bake")

    POST = LoadingStage("stage:post")


LOADING_ORDER = [LoadingStages.PREPARE, LoadingStages.ADD_LOADING_STAGES, LoadingStages.PREBUILD_TASKS,
                 LoadingStages.PREBUILD_DO, LoadingStages.EXTRA_RESOURCE_LOCATIONS, LoadingStages.TAG_GROUPS,
                 LoadingStages.TAGS, LoadingStages.BLOCK_BASES, LoadingStages.BLOCKS, LoadingStages.BLOCKS_OVERWRITE,
                 LoadingStages.ITEM_BASES, LoadingStages.ITEMS, LoadingStages.ITEMS_OVERWRITE, LoadingStages.LANGUAGE,
                 LoadingStages.RECIPE_GROUPS, LoadingStages.RECIPES, LoadingStages.INVENTORIES,
                 LoadingStages.STATEPARTS, LoadingStages.STATES, LoadingStages.MODEL_NOTATE,
                 LoadingStages.BLOCKSTATE_NOTATE, LoadingStages.MODEL_BAKE, LoadingStages.TEXTURE_ATLAS_BAKE,
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
            modlocations += [loc+"/"+x for x in os.listdir(loc)]
        for entry in modlocations:
            file = G.local+"/mods/{}".format(entry)
            if os.path.isfile(file):
                if zipfile.is_zipfile(file):  # compressed file
                    sys.path.append(file)
                    ResourceLocator.RESOURCE_LOCATIONS.append(ResourceLocator.ResourceZipFile(file))
                    self.active_directory = file
                    with zipfile.ZipFile(file) as f:
                        with f.open("mod.json", mode="r") as sf:
                            data = json.load(sf)
                        for location in data["main files"]:
                            importlib.import_module(location)
                elif file.endswith(".py"):  # python script file
                    self.active_directory = file
                    importlib.import_module("mods."+entry.split(".")[0])
            elif os.path.isdir(file) and "__pycache__" not in file:  # source directory
                sys.path.append(file)
                ResourceLocator.RESOURCE_LOCATIONS.append(ResourceLocator.ResourceDirectory(file))
                self.active_directory = file
                with open(file+"/mod.json") as sf:
                    data = json.load(sf)
                for location in data["main files"]:
                    importlib.import_module(location)
        print("found mods: {}".format(len(self.found_mods)))

    def add_to_add(self, mod):
        self.mods[mod.name] = mod
        self.found_mods.append(mod)
        mod.path = self.active_directory

    def sort_mods(self):
        modinfo = {}
        errors = []
        for mod in self.found_mods:
            if mod.name in modinfo:
                errors.append("-Mod {} has more than one version in the folder. Please load only every mod ONES")
            else:
                modinfo[mod.name] = set()
        for mod in self.found_mods:
            depends = mod.dependinfo[0][:]
            for depend in depends:
                if not depend.arrival():
                    errors.append("-Mod {} needs mod {} which is not provided".format(mod.name, depend))
            for depend in mod.dependinfo[2]:
                if depend.arrival():
                    errors.append("-Mod {} is incompatible with {}".format(mod.name, depend))
        for mod in self.found_mods:
            for depend in mod.dependinfo[4]:
                if depend.name in modinfo and depend.name not in modinfo[mod.name]:
                    modinfo[mod.name].add(depend.name)
            for depend in mod.dependinfo[3]:
                if depend.name in modinfo and mod.name not in modinfo[depend.name]:
                    modinfo[depend.name].add(mod.name)
        if len(errors) > 0:
            print("errors with mods:")
            print(" -", end="")
            print(*errors, sep="\n -")
            sys.exit(-1)
        sets = toposort.toposort(modinfo)
        sort = []
        for entry in sets:
            sort += list(entry)
        self.modorder = sort

    def process(self):
        start = time.time()
        while time.time() - start < 0.2:
            modname = self.modorder[self.active_loading_mod]
            mod = self.mods[modname]
            result = LOADING_ORDER[self.active_loading_stage].call_one(mod)
            if result == False:  # finished with mod
                self.active_loading_mod += 1
                if self.active_loading_mod >= len(self.modorder):
                    self.active_loading_mod = 0
                    self.active_loading_stage += 1
                    if self.active_loading_stage >= len(LOADING_ORDER):
                        G.statehandler.switch_to("minecraft:blockitemgenerator")
                        return
                    state.StateModLoading.modloading.parts[0].progress = self.active_loading_stage + 1
                    state.StateModLoading.modloading.parts[0].progress_max = len(LOADING_ORDER)
                    state.StateModLoading.modloading.parts[0].text = ", ".join(list(
                        LOADING_ORDER[self.active_loading_stage].eventnames))


G.modloader = ModLoader()


import mod.ModMcpython

