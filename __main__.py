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
import sys
import traceback

# everything lower than python 3.9 is not supported, we are using python 3.9 features!
# todo: bump to python 3.10 when all dependencies support it
if sys.version_info.major < 3 or sys.version_info.minor < 9:
    print(
        "[WARN] you are using an not supported version of python. Game will not be able to run!"
    )
    sys.exit(-1)

# LaunchWrapper is the system for launching the game
import mcpython.LaunchWrapper
wrapper = mcpython.LaunchWrapper.LaunchWrapper()


if __name__ == "__main__":
    try:
        wrapper.prepare_client()
        wrapper.print_header()
        wrapper.inject_sys_argv(sys.argv)  # load sys.argv
        wrapper.setup()  # do setup stuff
        wrapper.launch()  # and start mainloop
    except SystemExit:
        raise
    except:
        wrapper.error_clean()

        traceback.print_exc()

        sys.exit(-1)

    wrapper.clean()
