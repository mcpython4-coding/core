"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import os

local = os.path.dirname(__file__)

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

modelhandler = None

