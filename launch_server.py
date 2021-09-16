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

# everything lower than python 3.9 is not supported, we are using python 3.9 features!
if sys.version_info.major != 3 or sys.version_info.minor < 9:
    print(
        "[VERSION DETECTOR][FATAL] you are using an not supported version of python. "
        "You need at least python 3.9 in order to run the game!"
    )
    sys.exit(-1)

if sys.version_info.minor == 9:
    print(
        "[INTERNAL][WARN] You are using python 3.9 which will be unsupported in a handful of released"
    )
    print(
        "                 We made our game compatible with python 3.10 some releases ago, so please update!"
    )

if sys.version_info.minor >= 11:
    print(
        f"[VERSION DETECTOR][WARN] Detected python version 3.{sys.version_info.minor}, which is >= 11, which may break at any point"
    )

# the LaunchWrapper which launches all stuff
import mcpython.LaunchWrapper

wrapper = mcpython.LaunchWrapper.LaunchWrapper()


if __name__ == "__main__":
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
    except SystemExit:
        raise
    except:
        wrapper.error_clean()
        print("closing")
        sys.exit(-1)

    wrapper.clean()
