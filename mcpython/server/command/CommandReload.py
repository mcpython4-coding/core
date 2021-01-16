"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft, representing snapshot 20w51a
(https://www.minecraft.net/en-us/article/minecraft-snapshot-20w51a)

This project is not official by mojang and does not relate to it.
"""
import gc

from mcpython import shared
import mcpython.common.DataPack
import mcpython.server.command.Command
import mcpython.common.config
import mcpython.common.event.EventHandler
import mcpython.common.event.TickHandler
import mcpython.client.rendering.entities.EntityRenderer
import mcpython.client.rendering.util
from mcpython.server.command.Command import ParseBridge


@shared.registry
class CommandReload(mcpython.server.command.Command.Command):
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
        import mcpython.common.data.ResourcePipe

        mcpython.common.data.ResourcePipe.handler.reload_content()

    @staticmethod
    def get_help() -> list:
        return ["/reload: reloads the world"]


def reload_chunks():
    dim = shared.world.get_active_dimension()
    for i, chunk in enumerate(
        list(dim.chunks.values())
    ):  # iterate over all active chunks
        shared.window.set_caption(
            "preparing chunk {}/{} at {}".format(i + 1, len(dim.chunks), chunk.position)
        )
        chunk.update_visible(immediate=True)
    shared.window.set_caption("finished!")


mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "hotkey:chunk_reload", reload_chunks
)
mcpython.common.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "hotkey:reload_textures", CommandReload.reload
)
