"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import math

MC_VERSION_BASE = "1.15.2"
VERSION_TYPE = "dev"
# possible: [<pre>]<version>, <normal mc snapshot format>, snapshot dev <number of snapshot> cycle <cycle number>
VERSION_NAME = "snapshot dev 1 cycle 2"

# list of all versions since 19w52a to indicate order of release; used in save files todo: export to other file
VERSION_ORDER = ["19w52a", "20w05a", "20w07a", "20w09a", "20w10a", "20w11a", "20w12a", "20w12b", "20w14a",
                 "a1.0.0", "a1.0.1", "snapshot dev 1 cycle 1", VERSION_NAME]

FULL_VERSION_NAME = "mcpython version {} ({}) based on mc version {}".format(
    VERSION_NAME, VERSION_TYPE, MC_VERSION_BASE)

TICKS_PER_SEC = 20  # how many ticks per second should be executed

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
    3: [WALKING_SPEED, SPRINTING_SPEED, GAMEMODE_3_SPEED, GAMEMODE_3_SPRINTING_SPEED]
}

GRAVITY = 20.0  # gravity, in -m/s^2 -> speed is calculated with v -= GRAVITY * dt
TERMINAL_VELOCITY = 50  # maximum speed downwards
MAX_JUMP_HEIGHT = 1.0  # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)

PLAYER_HEIGHT = 2  # the height of the player, in blocks; WARNING: will be removed in the future


_ADVANCED_FACES = [[[(x, y, z) for z in range(-1, 2)] for y in range(-1, 2)] for x in range(-1, 2)]
ADVANCED_FACES = []
for e in _ADVANCED_FACES:
    for i in e:
        for m in e:
            for x in m:
                if any(m): ADVANCED_FACES.append(x)
del _ADVANCED_FACES


RANDOM_TICK_RANGE = 2  # how far to execute random ticks away from player

USE_MISSING_TEXTURES_ON_MISS_TEXTURE = False  # if missing texture should be used when no texture was selected for an face

CPU_USAGE_REFRESH_TIME = 0.8  # how often to refresh cpu usage indicator

FOG_DISTANCE = 60  # something like view distance, but will no force the chunks to generate


BIOME_HEIGHT_RANGE_MAP = {  # an dict of biomename: height range storing the internal height range
    "minecraft:plains": (10, 30)
}


# how far to generate chunks on sector change, in chunks from the chunk the player is in, in an square with
# CHUNK_GENERATION_RANGE * 2 + 1 -size
CHUNK_GENERATION_RANGE = 1

WRITE_NOT_FORMATTED_EXCEPTION = False  # if exceptions should be not formatted-printed to console by logger

