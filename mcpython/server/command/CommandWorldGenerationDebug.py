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
from mcpython import shared
from mcpython.server.command.Builder import Command, CommandNode, DefinedString


def ping(env):
    def p(context):
        print("ping")
        context.get_helper().run_on_main(lambda _: print("pong"))

        async def test(ctx):
            print("ping-pong")

        context.get_helper().run_on_process(test)

    env.get_dimension().get_world().world_generation_process.run_on_process(p)


worldgendebug = (
    Command("worldgendebug")
    .than(
        CommandNode(DefinedString("info"))
        .of_name("info")
        .info("gets information about the current world generation status")
        .on_execution(
            lambda env, data: print(
                env.get_dimension()
                .get_world()
                .world_generation_process.get_worker_count()
            )
        )
    )
    .than(
        CommandNode(DefinedString("ping"))
        .of_name("ping")
        .info("pings the world generation process")
        .on_execution(lambda env, data: ping(env))
    )
)
