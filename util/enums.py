"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
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

