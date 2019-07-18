"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4-pre6.jar"""
import os

local = os.path.dirname(__file__)

window = None
model = None
player = None

eventhandler = None
tickhandler = None

blockhandler = None
statehandler = None
texturefactoryhandler = None
inventoryhandler = None
itemhandler = None

modelloader = None


jar_archive = None
