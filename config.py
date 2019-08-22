"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import math


TICKS_PER_SEC = 60

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
    3: [None, None, GAMEMODE_3_SPEED, GAMEMODE_3_SPRINTING_SPEED]
}

GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.0 # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

PLAYER_HEIGHT = 2

TEXTURE_PATH = 'assets/texture.png'

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]


RANDOM_TICK_SPEED = 1
RANDOM_TICK_RANGE = 0

