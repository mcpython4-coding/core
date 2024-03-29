"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
import mcpython.engine.event.EventHandler
from mcpython import shared
from mcpython.server.command.Builder import Command


async def reload_func():
    import mcpython.common.data.ResourcePipe

    await mcpython.common.data.ResourcePipe.handler.reload_content()


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


mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "hotkey:chunk_reload", reload_chunks
)
mcpython.engine.event.EventHandler.PUBLIC_EVENT_BUS.subscribe(
    "hotkey:reload_textures", reload_func
)


reload = (
    Command("reload")
    .on_execution(lambda env, data: reload_func())
    .info("Reloads data packs")
)
