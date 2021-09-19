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

# LaunchWrapper is the system for launching the game
import mcpython.LaunchWrapper

wrapper = mcpython.LaunchWrapper.LaunchWrapper()
wrapper.check_py_version()


if __name__ == "__main__":
    from mcpython.engine import logger

    try:
        wrapper.set_client()
        wrapper.full_launch()

    except SystemExit:
        # this is here to fix some cleanup problems
        # os._exit(-1)
        raise
    except:
        wrapper.error_clean()

        traceback.print_exc()

        print("closing")
        sys.exit(-1)

    wrapper.clean()
