"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import subprocess
import sys


subprocess.Popen([sys.executable, "-m", "pip", "install", "-r", "./requirements.txt"],
                 stdout=sys.stdout, stderr=sys.stderr)
# subprocess.Popen([sys.executable, "./__main__.py", "--data-gen", "--exit-after-data-gen"], stdout=sys.stdout)
