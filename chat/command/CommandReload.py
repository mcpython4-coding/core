"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import event.TickHandler
import event.EventHandler
import gc
import chat.DataPack
import rendering.OpenGLSetupFile
import rendering.EntityRenderer


@G.registry
class CommandReload(chat.command.Command.Command):
    """
    class for /reload command
    """

    NAME = "minecraft:reload"

    CANCEL_RELOAD = False

    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "reload"

    @classmethod
    def parse(cls, values: list, modes: list, info):
        cls.reload()

    @classmethod
    def reload(cls):
        cls.CANCEL_RELOAD = False
        G.eventhandler.call("command:reload:start")
        if cls.CANCEL_RELOAD: return
        chat.DataPack.datapackhandler.reload()  # reloads all data packs
        G.taghandler.reload()  # reloads all tags
        G.craftinghandler.reload_crafting_recipes()  # reloads all recipes
        G.inventoryhandler.reload_config()  # reloads inventory configuration
        rendering.OpenGLSetupFile.FILES.clear()
        rendering.OpenGLSetupFile.execute_file_by_name("setup")  # re-setup opengl
        [e.reload() for e in rendering.EntityRenderer.RENDERERS]
        G.eventhandler.call("command:reload:end")
        gc.collect()  # make sure that memory was cleaned up

    @staticmethod
    def get_help() -> list:
        return ["/reload: reloads the world"]


def reload_chunks():
    dim = G.world.get_active_dimension()
    for i, chunk in enumerate(list(dim.chunks.values())):  # iterate over all active chunks
        G.window.set_caption("preparing chunk {}/{} at {}".format(i + 1, len(dim.chunks), chunk.position))
        chunk.update_visable(immediate=True)
    G.window.set_caption("finished!")


event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:chunk_reload", reload_chunks)
event.EventHandler.PUBLIC_EVENT_BUS.subscribe("hotkey:reload_textures", CommandReload.reload)

