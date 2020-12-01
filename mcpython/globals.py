"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import os, sys, tempfile
import mcpython.rendering.RenderingHelper
# todo: create MCPYTHON-class (as main game class) replacing this mess

prebuilding = "--rebuild" in sys.argv
debugevents = "--debugevents" in sys.argv
dev_environment = True  # dynamical set on build

local = os.path.dirname(__file__).replace("\\", "/")
home = local+"/home" if "--home-folder" not in sys.argv else sys.argv[sys.argv.index("--home-folder")+1]
build = home+"/build" if "--build-folder" not in sys.argv else sys.argv[sys.argv.index("--build-folder")+1]
tmp = tempfile.TemporaryDirectory()

data_gen = ("--data-gen" in sys.argv or "--rebuild" in sys.argv) and dev_environment
data_gen_exit = "--exit-after-data-gen" in sys.argv

STORAGE_VERSION = None

window = None
world = None

chat = None

eventhandler = None
tickhandler = None

registry = None
commandparser = None
statehandler = None
texturefactoryhandler = None
inventoryhandler = None
worldgenerationhandler = None
biomehandler = None
craftinghandler = None
taghandler = None
dimensionhandler = None
loottablehandler = None
entityhandler = None

modelhandler = None

modloader = None

rendering_helper = mcpython.rendering.RenderingHelper.RenderingHelper()

NEXT_EVENT_BUS_ID = 0

