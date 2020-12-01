"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
"""
WARNING: the system is outdated and will likely be removed in the future

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
import json
import os
import shutil

from mcpython import globals as G, logger
import mcpython.event.Registry
import mcpython.mod.ModMcpython


class IPrepareAbleTask(mcpython.event.Registry.IRegistryContent):
    TYPE = "minecraft:prebuild_task"

    @staticmethod
    def dump_data(directory: str): pass

    USES_DIRECTORY = True


taskregistry = mcpython.event.Registry.Registry("preparetasks", ["minecraft:prebuild_task"])


def add():
    @G.registry
    class Cleanup(IPrepareAbleTask):
        NAME = "cleanup"

        @staticmethod
        def dump_data(directory: str):
            for _ in range(10):
                try:
                    shutil.rmtree(G.build+"")
                    break
                except PermissionError: pass
                except OSError: pass
            else:
                raise IOError("can't remove 'build'-folder. please make sure that no file is opened")
            os.makedirs(G.build+"")

        USES_DIRECTORY = False

    @G.registry
    class TextureFactoryGenerate(IPrepareAbleTask):
        NAME = "texturefactory:prepare"

        @staticmethod
        def dump_data(directory: str):
            G.texturefactoryhandler.load()

        USES_DIRECTORY = False


def execute():
    if not os.path.exists(G.build+""):
        os.makedirs(G.build+"")
    with open(G.build+"/info.json", mode="w") as f:
        json.dump({"finished": False}, f)
    for iprepareabletask in taskregistry.registered_object_map.values():
        directory = G.build+"/"+iprepareabletask.NAME
        if iprepareabletask.USES_DIRECTORY:
            if os.path.exists(directory): shutil.rmtree(directory)
            os.makedirs(directory)
        iprepareabletask.dump_data(directory)
    G.eventhandler.call("prebuilding:finished")


# todo: split up into different sub-calls
mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:prebuild:addition", add, info="adding prebuild tasks")

if not os.path.exists(G.build+"/info.json"):
    logger.println("rebuild mode due missing info file")
    G.prebuilding = True
    G.data_gen = True
else:
    with open(G.build+"/info.json") as f:
        data = json.load(f)
    if not data["finished"]:
        logger.println("rebuild mode due to unfinished cache")
        G.prebuilding = True
        G.data_gen = True

if G.prebuilding:
    mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:prebuild:do", execute, info="doing prebuild tasks")
