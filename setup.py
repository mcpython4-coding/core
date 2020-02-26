"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
"""
what does this system do?
    as mentioned in #1 (may be closed when you read this), game loading takes / have taken for some reasons on some
        devices very long (in #1: 30 minutes).
    These file tries to fix this problem by adding an system which generates before the game is started by the user
        (or on his first start in an new downloaded folder) the things from different parts of the game which can be
        prepared before the game starts (texture atlases, file transformations, texture editing, ...) in an separated
        folder. Access to the prepared data is organized by index files.
    What happens if the user adds some data into the game?
        The system is not generating during runtime anymore. To update the data, run program with --rebuild or import
        the __main__ file and the setup file and call the functions by hand
        
    What happens if an mod loader should be added?
        Have a look what is done to generate the vanilla things. Try to give the mod an interface for generating things.
        Rerun mod specified and vanilla-adapting tasks when the mod with the given version was run first. Afterwards,
        only access the prepared data. 
"""
import globals as G
import event.Registry
import os
import shutil
import texture.factory
import mod.ModMcpython
import sys
import json
import event.Registry


class IPrepareAbleTask(event.Registry.IRegistryContent):
    TYPE = "minecraft:prebuild_task"

    @staticmethod
    def dump_data(directory: str): pass

    USES_DIRECTORY = True


taskregistry = event.Registry.Registry("preparetasks", ["minecraft:prebuild_task"])


def add():
    @G.registry
    class Cleanup(IPrepareAbleTask):
        NAME = "cleanup"

        @staticmethod
        def dump_data(directory: str):
            for _ in range(10):
                try:
                    shutil.rmtree(G.local+"/build")
                    break
                except PermissionError: pass
                except OSError: pass
            else:
                raise IOError("can't remove 'build'-folder. please make sure that no file is opened")
            os.makedirs(G.local+"/build")

        USES_DIRECTORY = False

    @G.registry
    class TextureFactoryGenerate(IPrepareAbleTask):
        NAME = "texturefactory:prepare"

        @staticmethod
        def dump_data(directory: str):
            G.texturefactoryhandler.load()

        USES_DIRECTORY = False


def execute():
    if not os.path.exists(G.local+"/build"):
        os.makedirs(G.local+"/build")
    with open(G.local+"/build/info.json", mode="w") as f:
        json.dump({"finished": False}, f)
    for iprepareabletask in taskregistry.registered_object_map.values():
        directory = G.local+"/build/"+iprepareabletask.NAME
        if iprepareabletask.USES_DIRECTORY:
            if os.path.exists(directory): shutil.rmtree(directory)
            os.makedirs(directory)
        iprepareabletask.dump_data(directory)
    G.eventhandler.call("prebuilding:finished")


# todo: split up into different sub-calls
mod.ModMcpython.mcpython.eventbus.subscribe("stage:prebuild:addition", add, info="adding prebuild tasks")

if not os.path.exists(G.local+"/build/info.json"): G.prebuilding = True
else:
    with open(G.local+"/build/info.json") as f:
        data = json.load(f)
    if not data["finished"]:
        G.prebuilding = True

if G.prebuilding:
    mod.ModMcpython.mcpython.eventbus.subscribe("stage:prebuild:do", execute, info="doing prebuild tasks")

