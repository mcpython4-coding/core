"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import sys
import logger
import globals as G

if sys.version_info.major < 3 or sys.version_info.minor < 7:  # everything lower is not supported!
    print("[WARN] you are using an not supported version of python. Game will not run!")
    sys.exit(-1)

import mcpython.LaunchWrapper


wrapper = mcpython.LaunchWrapper.LaunchWrapper()
try:
    wrapper.inject_sys_argv()
    wrapper.setup()
    wrapper.launch()
except SystemExit:
    sys.exit(-1)
except:
    # todo: move this part to LaunchWrapper as clean() function
    import mcpython.ResourceLocator

    mcpython.ResourceLocator.close_all_resources()
    logger.write_exception("general loading exception")
    try:
        G.tmp.cleanup()
    except NameError:
        pass
    sys.exit(-1)

# todo: move this part to LaunchWrapper as clean() function
import mcpython.ResourceLocator
mcpython.ResourceLocator.close_all_resources()
G.eventhandler.call("game:close")
G.tmp.cleanup()
