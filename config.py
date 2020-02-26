"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import math
import util.enums

MC_VERSION_BASE = "1.15.2"
VERSION_TYPE = "snapshot"
VERSION_NAME = "20w08a"
VERSION_ORDER = ["19w52a", "20w05a", "20w07a", "20w08a"]  # list of all versions since 19w52a to indicate order

FULL_VERSION_NAME = "mcpython version {} ({}) based on mc version {}".format(
    VERSION_NAME, VERSION_TYPE, MC_VERSION_BASE)


TICKS_PER_SEC = 20

WALKING_SPEED = 5
SPRINTING_SPEED = 8
FLYING_SPEED = 15
FLYING_SPRINTING_SPEED = 18
GAMEMODE_3_SPEED = 20
GAMEMODE_3_SPRINTING_SPEED = 25

SPEED_DICT = {
    0: [WALKING_SPEED, SPRINTING_SPEED],
    1: [WALKING_SPEED, SPRINTING_SPEED, FLYING_SPEED, FLYING_SPRINTING_SPEED],
    2: [WALKING_SPEED, SPRINTING_SPEED],
    3: [0, 0, GAMEMODE_3_SPEED, GAMEMODE_3_SPRINTING_SPEED]
}

GRAVITY = 20.0
TERMINAL_VELOCITY = 50
MAX_JUMP_HEIGHT = 1.0  # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)

PLAYER_HEIGHT = 2


_ADVANCED_FACES = [[[(x, y, z) for z in range(-1, 2)] for y in range(-1, 2)] for x in range(-1, 2)]
ADVANCED_FACES = []
for e in _ADVANCED_FACES:
    for i in e:
        for m in e:
            for x in m:
                if any(m): ADVANCED_FACES.append(x)
del _ADVANCED_FACES


RANDOM_TICK_SPEED = 3
RANDOM_TICK_RANGE = 2

USE_MISSING_TEXTURES_ON_MISS_TEXTURE = False

CPU_USAGE_REFRESH_TIME = 0.8

