"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import enum


class EnumSide(enum.Enum):
    TOP = UP = U = 0
    BOTTOM = DOWN = D = 1
    NORTH = N = 2
    EAST = E = 3
    SOUTH = S = 4
    WEST = W = 5


SIDE_ORDER = [EnumSide.U, EnumSide.D, EnumSide.E, EnumSide.W, EnumSide.N, EnumSide.S]

NAMED_SIDES = {"up": EnumSide.U, "down": EnumSide.D, "north": EnumSide.N, "east": EnumSide.EAST,
               "south": EnumSide.S, "west": EnumSide.W}


class LogAxis(enum.Enum):
    X = 0
    Y = 1
    Z = 2


class ToolType(enum.Enum):
    HAND = 0
    PICKAXE = 1
    AXE = 2
    SHOVEL = 3
    SHEAR = 4
    SWORD = 5  # not real an tool, but internally handled as one of it
    HOE = 6  # not real an tool, but internally handled as one of it


class SlabModes(enum.Enum):
    TOP = 1
    BOTTOM = 2
    DOUBLE = 3


class LoadingStageStatus(enum.Enum):
    WORKING = 0
    MOD_CHANGED = 1
    EVENT_CHANGED = 2
    FINISHED = 3


class ButtonMode(enum.Enum):
    DISABLED = 0
    ENABLED = 1
    HOVERING = 2

