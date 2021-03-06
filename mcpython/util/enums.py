"""
mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang Studios (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

This project is not official by mojang and does not relate to it.
"""
import enum
import typing
import itertools

COLORS = [
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
]


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
        return INVERTED_DICT[self.normal_name]

    def relative_offset(self, position):
        relative = self.relative
        return tuple([position[i] + relative[i] for i in range(3)])

    def __eq__(self, other):
        return type(self) == type(other) and self.normal_name == other.normal_name

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

    def as_bit(self) -> int:
        return 2 ** FACE_ORDER.index(self)


FACE_ORDER: typing.List[EnumSide] = [
    EnumSide.UP,
    EnumSide.DOWN,
    EnumSide.NORTH,
    EnumSide.SOUTH,
    EnumSide.EAST,
    EnumSide.WEST,
]

# How to rotate the different faces?
ROTATE: typing.List[typing.List[EnumSide]] = [
    [EnumSide.WEST, EnumSide.DOWN, EnumSide.EAST, EnumSide.UP],
    [EnumSide.NORTH, EnumSide.EAST, EnumSide.SOUTH, EnumSide.WEST],
    [EnumSide.NORTH, EnumSide.UP, EnumSide.SOUTH, EnumSide.DOWN],
]

INVERTED_DICT: typing.Dict[str, EnumSide] = {
    EnumSide.U.normal_name: EnumSide.D,
    EnumSide.D.normal_name: EnumSide.U,
    EnumSide.N.normal_name: EnumSide.S,
    EnumSide.S.normal_name: EnumSide.N,
    EnumSide.E.normal_name: EnumSide.W,
    EnumSide.W.normal_name: EnumSide.E,
}


HORIZONTAL_OFFSETS = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]


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


class NormalWoodTypes(enum.Enum):
    ACACIA = "acacia"
    BIRCH = "birch"
    SPRUCE = "spruce"
    JUNGLE = "jungle"
    OAK = "oak"
    DARK_OAK = "dark_oak"

    def __init__(self, name: str):
        self.data_name = name

    def __hash__(self):
        return hash(self.data_name)

    def __eq__(self, other):
        return self.data_name == other.data_name

    def __repr__(self):
        return self.data_name


class NetherWoodTypes(enum.Enum):
    CRIMSON = "crimson"
    WARPED = "warped"

    def __init__(self, name: str):
        self.data_name = name

    def __hash__(self):
        return hash(self.data_name)

    def __eq__(self, other):
        return self.data_name == other.data_name

    def __repr__(self):
        return self.data_name


def all_woods():
    return itertools.chain(NormalWoodTypes.__iter__(), NetherWoodTypes.__iter__())
