"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import os, sys, tempfile

prebuilding = "--rebuild" in sys.argv
debugevents = "--debugevents" in sys.argv

local = os.path.dirname(__file__).replace("\\", "/")
tmp = tempfile.TemporaryDirectory()

STORAGE_VERSION = None

window = None
world = None
player = None

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

modelhandler = None

modloader = None

NEXT_EVENT_BUS_ID = 0

