"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import gc

from mcpython import globals as G
import mcpython.chat.DataPack
import mcpython.chat.command.Command
import mcpython.config
import mcpython.event.EventHandler
import mcpython.event.TickHandler
import mcpython.rendering.EntityRenderer
import mcpython.rendering.OpenGLSetupFile
from mcpython.chat.command.Command import ParseBridge
import subprocess
import sys


@G.registry
class CommandReload(mcpython.chat.command.Command.Command):
    """
    class for /reload command
    """

    NAME = "minecraft:reload"

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "reload"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        cls.reload()

    @classmethod
    def reload(cls):
        G.window.print_profiler()  # print the profiler's
        if not G.eventhandler.call_cancelable("data:reload:cancel"): return
        mcpython.chat.DataPack.datapackhandler.reload()  # reloads all data packs
        G.taghandler.reload()  # reloads all tags
        G.craftinghandler.reload_crafting_recipes()  # reloads all recipes
        G.loottablehandler.reload()

        # as we are reloading, this may get mixed up...
        G.craftinghandler.recipe_relink_table.clear()
        G.loottablehandler.relink_table.clear()
        G.eventhandler.call("data:shuffle:clear")
        if mcpython.config.SHUFFLE_DATA:  # .. and we need to re-do if needed
            G.eventhandler.call("data:shuffle:all")

        G.inventoryhandler.reload_config()  # reloads inventory configuration
        G.modelhandler.reload_models()
        mcpython.rendering.OpenGLSetupFile.FILES.clear()  # remove all loaded OpenGL conifg ifles
        mcpython.rendering.OpenGLSetupFile.execute_file_by_name("setup")  # re-setup opengl
        # todo: regenerate block item images, regenerate item atlases

        # reload entity model files
        [e.reload() for e in mcpython.rendering.EntityRenderer.RENDERERS]

        G.eventhandler.call("data:reload:work")

        gc.collect()  # make sure that memory was cleaned up
        G.window.print_profiler()  # and now print the profile's (if needed)

    @staticmethod
    def get_help() -> list:
        return ["/reload: reloads the world"]


def reload_chunks():
    dim = G.world.get_active_dimension()
    for i, chunk in enumerate(list(dim.chunks.values())):  # iterate over all active chunks
        G.window.set_caption("preparing chunk {}/{} at {}".format(i + 1, len(dim.chunks), chunk.position))
        chunk.update_visible(immediate=True)
    G.window.set_caption("finished!")


mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:chunk_reload", reload_chunks)
mcpython.event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:reload_textures", CommandReload.reload)
