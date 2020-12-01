"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import subprocess
import sys
import os
"""
installation code for setting up your python
"""

home = os.path.dirname(os.path.dirname(__file__))


subprocess.Popen([sys.executable, "-m", "pip", "install", "-r", "./requirements.txt"],
                 stdout=sys.stdout, stderr=sys.stderr)
# THE FOLLOWING LINE IS  O N L Y  PRESENT IN DEV ENVIRONMENT
subprocess.Popen([sys.executable, home+"/__main__.py", "--data-gen", "--exit-after-data-gen", "--no-window"], stdout=sys.stdout)

