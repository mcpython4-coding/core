"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import event.TickHandler
import event.EventHandler
import gc
import chat.DataPack


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
        G.craftinghandler.reload_crafting_recipes()
        G.inventoryhandler.reload_config()
        event.TickHandler.handler.bind(G.window.reset_caption, 20)
        chat.DataPack.datapackhandler.reload()
        G.eventhandler.call("command:reload:end")
        gc.collect()

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

