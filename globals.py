"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import os, sys, tempfile

prebuilding = "--rebuild" in sys.argv
debugevents = "--debugevents" in sys.argv

local = os.path.dirname(__file__).replace("\\", "/")
home = local+"/home" if "--home" not in sys.argv else sys.argv[sys.argv.index("--home")+1]
tmp = tempfile.TemporaryDirectory()

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

NEXT_EVENT_BUS_ID = 0

