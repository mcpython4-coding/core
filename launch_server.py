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
# Special LaunchWrapper configuration for dedicated servers
# launches up only the server stuff

import sys

# the LaunchWrapper which launches all stuff
import mcpython.LaunchWrapper

wrapper = mcpython.LaunchWrapper.LaunchWrapper()


if __name__ == "__main__":
    wrapper.apply_mixins()
    wrapper.check_py_version()

    print(
        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )
    import mcpython.engine.logger

    mcpython.engine.logger.println(
        "[EXPERIMENTAL][WARN] launching experimental dedicated mcpython server"
    )
    mcpython.engine.logger.println(
        "[EXPERIMENTAL][WARN] see version.info and git diffs for recent changes"
    )
    print(
        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )

    try:
        wrapper.set_server()
        wrapper.full_launch()
    except (SystemExit, KeyboardInterrupt):
        raise
    except:
        wrapper.error_clean()
        print("closing")
        sys.exit(-1)

    wrapper.clean()
