"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import math
import sys

MC_VERSION_BASE = "1.16.1"
VERSION_TYPE = "dev"
# possible: [<pre>]<version>, <normal mc snapshot format>, snapshot dev <number of snapshot> cycle <cycle number>
VERSION_NAME = "snapshot dev 4"

DEVELOPING_FOR = "20w26a"
DEVELOPMENT_COUNTER = 3

# list of all versions since 19w52a to indicate order of release; used in save files todo: export to other file
VERSION_ORDER = ["19w52a", "20w05a", "20w07a", "20w09a", "20w10a", "20w11a", "20w12a", "20w12b", "20w14a",
                 "a1.0.0", "a1.0.1", "snapshot dev 1 cycle 1", "snapshot dev 1 cycle 2",
                 "snapshot dev 1 cycle 3", "snapshot dev 1 cycle 4", "20w22a", "snapshot dev 1",
                 "snapshot dev 2", "20w24a", "snapshot dev 3", "20w25a", VERSION_NAME]

FULL_VERSION_NAME = "mcpython version {} ({}) based on mc version {}".format(
    VERSION_NAME, VERSION_TYPE, MC_VERSION_BASE)

TICKS_PER_SEC = 20  # how many ticks per second should be executed, todo: remove (unused)

# todo: remove definitions of "raw" values
WALKING_SPEED = 5
SPRINTING_SPEED = 8
FLYING_SPEED = 15
FLYING_SPRINTING_SPEED = 18
GAMEMODE_3_SPEED = 20
GAMEMODE_3_SPRINTING_SPEED = 25

SPEED_DICT = {
    0: [WALKING_SPEED, SPRINTING_SPEED, 0, 0],
    1: [WALKING_SPEED, SPRINTING_SPEED, FLYING_SPEED, FLYING_SPRINTING_SPEED],
    2: [WALKING_SPEED, SPRINTING_SPEED, 0, 0],
    3: [FLYING_SPEED, FLYING_SPRINTING_SPEED, GAMEMODE_3_SPEED, GAMEMODE_3_SPRINTING_SPEED]
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

PLAYER_HEIGHT = 2  # the height of the player, in blocks; WARNING: will be removed in the future todo: remove


# todo: move to util.enums
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

USE_MIP_MAPPING = True

CPU_USAGE_REFRESH_TIME = 0.8  # how often to refresh cpu usage indicator

FOG_DISTANCE = 60  # something like view distance, but will no force the chunks to generate


BIOME_HEIGHT_RANGE_MAP = {  # an dict of biomename: height range storing the internal height range
    "minecraft:plains": (10, 30)
}


# how far to generate chunks on sector change, in chunks from the chunk the player is in, in an square with
# CHUNK_GENERATION_RANGE * 2 + 1 -size
CHUNK_GENERATION_RANGE = 1

WRITE_NOT_FORMATTED_EXCEPTION = False  # if exceptions should be not formatted-printed to console by logger

ENABLE_PROFILING = False

ENABLE_PROFILER_DRAW = True
ENABLE_PROFILER_TICK = False
ENABLE_PROFILER_GENERATION = False

SHUFFLE_DATA = False
SHUFFLE_INTERVAL = -1

"""
an list of additional blocks to enable/disable when needed
WARNING: this content is generated ONTOP of minecraft's content an uses their textures to generate. Please note
         that any of these objects look like original ones, but they are not (currently)
WARNING: All additional blocks have currently no own loot table for drops. These might change in the future,
         but until than, they are PURELY decorative blocks
WARNING: As these blocks are not part of the "normal" game, when they are enabled, they may NOT have the same
         behaviour flags build-in than the original ones (think about how an sand slab would behave)
WARNING: block behaviour is mostly copied from base block and as so, e.g. bedrock slabs are unbreakable in survival

WARNING (for modders): You might add your own entries onto this table. But make sure that you DO CHECK if they are
                       in the table when you read for block creation. Also note, these file is located in the 
                       minecraft-folder of the config folder.
"""

ENABLED_EXTRA_BLOCKS = {
    "minecraft:bedrock_slab": False, "minecraft:bedrock_wall": False, "minecraft:terracotta_slab": False,
    "minecraft:terracotta_wall": False, "minecraft:glass_slab": False, "minecraft:glass_wall": False,
    "minecraft:chiseled_polished_blackstone_slab": False, "minecraft:chiseled_polished_blackstone_wall": False,
    "minecraft:cracked_polished_blackstone_brick_slab": False, "minecraft:chiseled_nether_brick_slab": False,
    "minecraft:cracked_polished_blackstone_brick_wall": False, "minecraft:chiseled_nether_brick_wall": False,
    "minecraft:cracked_nether_brick_slab": False, "minecraft:cracked_nether_brick_wall": False,
    "minecraft:quartz_brick_slab": False, "minecraft:quartz_brick_wall": False, "minecraft:smooth_quart_wall": False,
    "minecraft:chiseled_stone_brick_slab": False, "minecraft:chiseled_stone_brick_wall": False,
    "minecraft:clay_slab": False, "minecraft:clay_wall": False, "minecraft:coal_block_slab": False,
    "minecraft:coal_block_wall": False, "minecraft:coarse_dirt_slab": False, "minecraft:coarse_dirt_wall": False,
    "minecraft:cracked_stone_brick_slab": False, "minecraft:cracked_stone_brick_wall": False,
    "minecraft:end_stone_slab": False, "minecraft:end_stone_wall": False, "minecraft:stone_wall": False,
    "minecraft:crying_obsidian_slab": False, "minecraft:crying_obsidian_wall": False, "minecraft:obsidian_slab": False,
    "minecraft:obsidian_wall": False, "minecraft:dark_prismarine_wall": False, "minecraft:prismarine_brick_wall": False,
    "minecraft:diamond_block_slab": False, "minecraft:diamond_block_wall": False, "minecraft:dirt_slab": False,
    "minecraft:dirt_wall": False, "minecraft:emerald_block_slab": False, "minecraft:emerald_block_wall": False,
    "minecraft:glowstone_slab": False, "minecraft:glowstone_wall": False, "minecraft:gold_block_slab": False,
    "minecraft:gold_block_wall": False, "minecraft:honeycomb_block_slab": False, "minecraft:iron_block_slab": False,
    "minecraft:honeycomb_block_wall": False, "minecraft:iron_block_wall": False, "minecraft:lapis_block_slab": False,
    "minecraft:lapis_block_wall": False, "minecraft:magma_block_slab": False, "minecraft:magma_block_wall": False,
    "minecraft:nether_wart_block_slab": False, "minecraft:nether_wart_block_wall": False,
    "minecraft:netherite_block_slab": False, "minecraft:netherite_block_wall": False,
    "minecraft:purpur_block_wall": False, "minecraft:redstone_block_slab": False, "minecraft:shroomlight_slab": False,
    "minecraft:redstone_block_wall": False, "minecraft:shroomlight_wall": False, "minecraft:snow_block_wall": False,
    "minecraft:soul_sand_slab": False, "minecraft:soul_sand_wall": False
}

# I'm to lazy to write these...
for wood in ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]:
    pass

for wood in ["crimson", "warped"]:
    pass

for wood in ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "crimson", "warped"]:
    ENABLED_EXTRA_BLOCKS["minecraft:{}_wall".format(wood)] = False

for color in ["white", "orange", "magenta", "light_blue", "lime", "pink", "gray", "light_gray", "cyan",
              "purple", "blue", "brown", "green", "red", "black"]:
    ENABLED_EXTRA_BLOCKS["minecraft:{}_concrete_slab".format(color)] = False
    ENABLED_EXTRA_BLOCKS["minecraft:{}_concrete_wall".format(color)] = False
    ENABLED_EXTRA_BLOCKS["minecraft:{}_terracotta_slab".format(color)] = False
    ENABLED_EXTRA_BLOCKS["minecraft:{}_terracotta_wall".format(color)] = False
    ENABLED_EXTRA_BLOCKS["minecraft:{}_wool_slab".format(color)] = False
    ENABLED_EXTRA_BLOCKS["minecraft:{}_wool_wall".format(color)] = False
    ENABLED_EXTRA_BLOCKS["minecraft:{}_stained_glass_slab".format(color)] = False
    ENABLED_EXTRA_BLOCKS["minecraft:{}_stained_glass_wall".format(color)] = False

for stone in ["andesite", "granite", "diorite"]:
    ENABLED_EXTRA_BLOCKS["minecraft:polished_{}_wall".format(stone)] = False


def load():
    import mcpython.mod.ConfigFile
    import globals as G

    config = mcpython.mod.ConfigFile.ConfigFile("main", "minecraft")
    speeds = mcpython.mod.ConfigFile.DictDataMapper().add_entry("walking", 5).add_entry("sprinting", 8).add_entry(
        "flying", 15).add_entry("fly_sprinting", 18).add_entry("gamemode_3", 20).add_entry("gamemode_3_sprinting", 25)
    physics = mcpython.mod.ConfigFile.DictDataMapper().add_entry("gravity", 20).add_entry("terminal_velocity", 50)
    timing = mcpython.mod.ConfigFile.DictDataMapper().add_entry("random_tick_range", 2).add_entry(
        "cpu_usage_refresh_time", .8)
    rendering = mcpython.mod.ConfigFile.DictDataMapper().add_entry("use_missing_texture_on_missing_faces",
                                                                   False).add_entry(
        "fog_distance", 60).add_entry("chunk_generation_range", 1).add_entry("write_not_formatted_exceptions", False)
    profiler = mcpython.mod.ConfigFile.DictDataMapper().add_entry("enable", False).add_entry(
        "total_draw", True).add_entry("total_tick", False).add_entry("generation", False)
    misc = mcpython.mod.ConfigFile.DictDataMapper().add_entry("enable_mixing_data", False).add_entry(
        "auto_shuffle_interval", -1)

    config.add_entry("physics", physics).add_entry("speeds", speeds).add_entry("timing", timing).add_entry(
        "rendering", rendering).add_entry("profiler", profiler).add_entry("misc", misc)

    biomeconfig = mcpython.mod.ConfigFile.ConfigFile("biomes", "minecraft")
    biomeconfig.add_entry("minecraft:plains", mcpython.mod.ConfigFile.ListDataMapper().append(10).append(30))

    block_config = mcpython.mod.ConfigFile.ConfigFile("blocks", "minecraft")
    [block_config.add_entry(key, mcpython.mod.ConfigFile.BooleanDataMapper()) for key in ENABLED_EXTRA_BLOCKS]

    @G.modloader("minecraft", "stage:mod:config:work")
    def load_data():
        SPEED_DICT[0] = [speeds["walking"].read(), speeds["sprinting"].read(), 0, 0]
        SPEED_DICT[1] = [speeds["walking"].read(), speeds["sprinting"].read(),
                         speeds["flying"].read(), speeds["fly_sprinting"].read()]
        SPEED_DICT[2] = [speeds["walking"].read(), speeds["sprinting"].read(), 0, 0]
        SPEED_DICT[3] = [speeds["flying"].read(), speeds["fly_sprinting"].read(),
                         speeds["gamemode_3"].read(), speeds["gamemode_3_sprinting"].read()]

        global GRAVITY, TERMINAL_VELOCITY
        GRAVITY, TERMINAL_VELOCITY = physics["gravity"].read(), physics["terminal_velocity"].read()

        global RANDOM_TICK_RANGE, CPU_USAGE_REFRESH_TIME
        RANDOM_TICK_RANGE, CPU_USAGE_REFRESH_TIME = timing["random_tick_range"].read(), timing[
            "cpu_usage_refresh_time"].read()

        global USE_MISSING_TEXTURES_ON_MISS_TEXTURE, FOG_DISTANCE, CHUNK_GENERATION_RANGE, WRITE_NOT_FORMATTED_EXCEPTION
        USE_MISSING_TEXTURES_ON_MISS_TEXTURE = rendering["use_missing_texture_on_missing_faces"].read()
        FOG_DISTANCE, CHUNK_GENERATION_RANGE = rendering["fog_distance"].read(), rendering["chunk_generation_range"
                                                                                           ].read()
        WRITE_NOT_FORMATTED_EXCEPTION = rendering["write_not_formatted_exceptions"].read()

        global BIOME_HEIGHT_RANGE_MAP
        BIOME_HEIGHT_RANGE_MAP["minecraft:plains"] = biomeconfig["minecraft:plains"].read()

        global ENABLE_PROFILING, ENABLE_PROFILER_DRAW, ENABLE_PROFILER_TICK, ENABLE_PROFILER_GENERATION
        ENABLE_PROFILING = profiler["enable"].read()
        ENABLE_PROFILER_DRAW = profiler["total_draw"].read()
        ENABLE_PROFILER_TICK = profiler["total_tick"].read()
        ENABLE_PROFILER_GENERATION = profiler["generation"].read()

        global SHUFFLE_DATA, SHUFFLE_INTERVAL
        SHUFFLE_DATA = misc["enable_mixing_data"].read()
        SHUFFLE_INTERVAL = misc["auto_shuffle_interval"].read()

        if SHUFFLE_DATA and SHUFFLE_INTERVAL > 0:
            import pyglet

            def on_shuffle(dt):
                import logger
                if G.world.world_loaded:
                    logger.println("shuffling data...")
                    G.eventhandler.call("data:shuffle:all")

            pyglet.clock.schedule_interval(on_shuffle, SHUFFLE_INTERVAL)

        if "--enable-all-blocks" not in sys.argv:
            for key in ENABLED_EXTRA_BLOCKS:
                ENABLED_EXTRA_BLOCKS[key] = block_config[key].read()
        else:  # we want to enable ALL without writing them to the config file
            for key in ENABLED_EXTRA_BLOCKS:
                ENABLED_EXTRA_BLOCKS[key] = True

        # todo: add doc strings into config files

