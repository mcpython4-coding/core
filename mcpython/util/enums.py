"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import enum

COLORS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan",
          "purple", "blue", "brown", "green", "red", "black"]


class EnumSide(enum.Enum):
    """
    Enum holding the 6 different sides of an Block.
    Also used for defining axis where it points in the direction
    """

    TOP = UP = U = (0, 1, 0, "up")
    BOTTOM = DOWN = D = (0, -1, 0, "down")
    NORTH = N = (-1, 0, 0, "north")
    EAST = E = (0, 0, 1, "east")
    SOUTH = S = (1, 0, 0, "south")
    WEST = W = (0, 0, -1, "west")

    @classmethod
    def iterate(cls):
        """
        Iterator for the faces
        """
        return FACE_ORDER

    def __init__(self, dx: int, dy: int, dz: int, normal_name: str):
        """
        Constructs an new enum instance
        :param dx: the delta in x
        :param dy: the delta in y
        :param dz: the delta in z
        :param normal_name: the normal name of the face
        """
        self.relative = self.dx, self.dy, self.dz = dx, dy, dz
        self.normal_name = normal_name

    def invert(self):
        """
        Will invert the face to its opposite
        :return: the opposite face
        """
        if self == EnumSide.U: return EnumSide.D
        if self == EnumSide.D: return EnumSide.U
        if self == EnumSide.N: return EnumSide.S
        if self == EnumSide.S: return EnumSide.S
        if self == EnumSide.E: return EnumSide.W
        if self == EnumSide.W: return EnumSide.E
        raise ValueError("can't convert '{}' to inverted variant".format(self))

    def __eq__(self, other):
        return type(self) == type(other) and self.relative == other.relative

    def __hash__(self):
        return hash(self.relative)

    def rotate(self, rotation: tuple):
        face = self
        for i in range(3):
            if face in ROTATE[i]:
                index = ROTATE[i].index(face)
                index += rotation[i] // 90
                index %= 4
                face = ROTATE[i][index]
        return face

    def rotate_reverse(self, rotation: tuple):
        face = self
        for i in range(3):
            if face in ROTATE[i]:
                index = ROTATE[i].index(face)
                index -= rotation[i] // 90
                index %= 4
                face = ROTATE[i][index]
        return face


FACE_ORDER = [EnumSide.UP, EnumSide.DOWN, EnumSide.NORTH, EnumSide.SOUTH, EnumSide.EAST, EnumSide.WEST]

# How to rotate the different faces?
ROTATE = ([EnumSide.WEST, EnumSide.DOWN, EnumSide.EAST, EnumSide.UP],
          [EnumSide.NORTH, EnumSide.EAST, EnumSide.SOUTH, EnumSide.WEST],
          [EnumSide.NORTH, EnumSide.UP, EnumSide.SOUTH, EnumSide.DOWN])


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

    # tool levels (from 0 to 6): hand, wood, stone, iron, gold, diamond, netherite


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

