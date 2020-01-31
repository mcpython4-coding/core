"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import ParseBridge, ParseType, ParseMode, SubCommand
import event.TickHandler


@G.registry
class CommandReload(chat.command.Command.Command):
    """
    class for /reload command
    """
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        parsebridge.main_entry = "reload"

    @staticmethod
    def parse(values: list, modes: list, info):
        G.eventhandler.call("command:reload:start")
        dim = G.world.get_active_dimension()
        for i, chunk in enumerate(list(dim.chunks.values())):  # iterate over all active chunks
            G.window.set_caption("preparing chunk {}/{} at {}".format(i+1, len(dim.chunks), chunk.position))
            chunk.update_visable(immediate=True)
        G.window.set_caption("finished!")
        G.craftinghandler.reload_crafting_recipes()
        G.inventoryhandler.reload_config()
        event.TickHandler.handler.bind(G.window.reset_caption, 20)
        G.eventhandler.call("command:reload:end")

    @staticmethod
    def get_help() -> list:
        return ["/reload: reloads the world"]

