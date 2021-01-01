"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
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


try:
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
