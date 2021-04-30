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
if sys.version_info.major < 3 or sys.version_info.minor < 9:
    print(
        "[WARN] you are using an not supported version of python. Game will not be able to run!"
    )
    sys.exit(-1)

# the LaunchWrapper which launches all stuff
import mcpython.LaunchWrapper

wrapper = mcpython.LaunchWrapper.LaunchWrapper()


if __name__ == "__main__":
    print(
        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )
    import mcpython.logger

    mcpython.logger.println(
        "[EXPERIMENTAL][WARN] launching experimental dedicated mcpython server"
    )
    mcpython.logger.println(
        "[EXPERIMENTAL][WARN] see version.info and git diffs for recent changes"
    )
    print(
        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )

    try:
        wrapper.prepare_server()

        wrapper.print_header()
        wrapper.inject_sys_argv(sys.argv)  # load sys.argv
        wrapper.setup()  # do setup stuff
        wrapper.launch()  # and start mainloop
    except SystemExit:
        sys.exit(-1)
    except:
        wrapper.error_clean()
        sys.exit(-1)

    wrapper.clean()
