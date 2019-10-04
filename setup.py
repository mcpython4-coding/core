"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
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


class IPrepareAbleTask:
    @staticmethod
    def get_name() -> str: raise NotImplementedError()

    @staticmethod
    def get_version() -> tuple: raise NotImplementedError()

    @staticmethod
    def dump_data(directory: str): pass

    @staticmethod
    def uses_directory() -> bool: return True


taskregistry = event.Registry.Registry("preparetasks", [IPrepareAbleTask])


@G.registry
class Cleanup(IPrepareAbleTask):
    @staticmethod
    def get_name() -> str: return "cleanup"

    @staticmethod
    def get_version() -> tuple: return 1, 0, 0

    @staticmethod
    def dump_data(directory: str):
        if os.path.exists(G.local+"/build"):
            shutil.rmtree(G.local+"/build")
        os.makedirs(G.local+"/build")

    @staticmethod
    def uses_directory() -> bool: return False


@G.registry
class TextureFactoryGenerate(IPrepareAbleTask):
    @staticmethod
    def get_name() -> str:
        return "texturefactory:prepare"

    @staticmethod
    def get_version() -> tuple: return 1, 0, 0

    @staticmethod
    def dump_data(directory: str):
        G.texturefactoryhandler.load()

    @staticmethod
    def uses_directory() -> bool: return False


def execute():
    for iprepareabletask in taskregistry.registered_objects:
        directory = G.local+"/build/"+iprepareabletask.get_name()
        if os.path.exists(directory): shutil.rmtree(directory)
        if iprepareabletask.uses_directory(): os.makedirs(directory)
        iprepareabletask.dump_data(directory)


