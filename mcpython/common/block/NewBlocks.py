"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
from mcpython import shared
from mcpython.common.event.DeferredRegistryHelper import DeferredRegistry
from mcpython.common.factory.BlockFactory import BlockFactory
from mcpython.common.factory.combined.complex import create_full_slab_wall_set
from mcpython.common.factory.combined.simple import CombinedFactoryInstance

"""
Missing:
air
attached_melon_stem
attached_pumpkin_stem
"""

DEFERRED_PIPE: DeferredRegistry = shared.registry.get_by_name(
    "minecraft:block"
).create_deferred("minecraft", base_factory=BlockFactory)


def plant(name: str):
    return (
        BlockFactory()
        .set_name(name)
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0)
    )


def wood(name: str, normal=True):
    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_button")
        .set_default_model_state("face=ceiling,facing=east,powered=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
    )
    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_door")
        .set_default_model_state("facing=east,half=lower,hinge=left,open=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
    )
    DEFERRED_PIPE.create_later(
        BlockFactory().set_name(f"minecraft:{name}_fence").set_fence().set_strength(0.5)
    )
    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_fence_gate")
        .set_fence_gate()
        .set_strength(0.5)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory().set_name(f"minecraft:{name}_planks").set_strength(2)
    )
    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_pressure_plate")
        .set_default_model_state("powered=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
    )
    DEFERRED_PIPE.create_later(
        BlockFactory().set_name(f"minecraft:{name}_slab").set_slab().set_strength(2)
    )

    if normal:
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:{name}_leaves")
            .set_solid(False)
            .set_all_side_solid(False)
            .set_strength(0.2)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory().set_name(f"minecraft:{name}_log").set_log().set_strength(2)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory().set_name(f"minecraft:{name}_wood").set_log().set_strength(2)
        )
        DEFERRED_PIPE.create_later(plant(f"minecraft:{name}_sapling"))

    CombinedFactoryInstance(
        f"minecraft:{name}_wall",
        f"minecraft:block/{name}_planks",
        deferred_registry=DEFERRED_PIPE,
    ).create_wall(suffix="_wall")

    # todo: signs, stairs


def stone_like(
    name: str,
    existing_full=True,
    existing_slab=True,
    existing_wall=True,
    existing_stairs=True,
    existing_fence=False,
    texture=None,
):
    fname = name.removesuffix("s")
    instance = CombinedFactoryInstance(
        f"minecraft:{name}",
        f"minecraft:block/{name}" if texture is None else texture,
        deferred_registry=DEFERRED_PIPE,
    )

    if existing_full:
        DEFERRED_PIPE.create_later(BlockFactory().set_name(f"minecraft:{name}"))
    else:
        instance.create_full_block()

    if existing_slab:
        DEFERRED_PIPE.create_later(
            BlockFactory().set_name(f"minecraft:{fname}_slab").set_slab()
        )
    else:
        instance.create_slab_block("_slab")

    if existing_wall:
        DEFERRED_PIPE.create_later(
            BlockFactory().set_name(f"minecraft:{fname}_wall").set_wall()
        )
    else:
        instance.create_wall("_wall")

    if existing_stairs:
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:{fname}_stairs")
            .set_default_model_state("facing=east,half=bottom,shape=inner_left")
            .set_solid(False)
            .set_all_side_solid(False)
        )
    else:
        pass  # todo: implement

    if existing_fence:
        DEFERRED_PIPE.create_later(
            BlockFactory().set_name(f"minecraft:{fname}_fence").set_fence()
        )
    else:
        instance.create_fence("_fence")


def colored(name: str):
    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_banner")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_bed")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_candle")
        .set_default_model_state("candles=4,lit=false")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_candle_cake")
        .set_default_model_state("lit=false")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    DEFERRED_PIPE.create_later(BlockFactory().set_name(f"minecraft:{name}_concrete"))

    DEFERRED_PIPE.create_later(
        BlockFactory().set_name(f"minecraft:{name}_concrete_powder").set_fall_able()
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_glazed_terracotta")
        .set_default_model_state("facing=east")
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_stained_glass")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    # todo: glass pane

    DEFERRED_PIPE.create_later(BlockFactory().set_name(f"minecraft:{name}_terracotta"))

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_wall_banner")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    DEFERRED_PIPE.create_later(BlockFactory().set_name(f"minecraft:{name}_wool"))


wood("acacia")

DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:activator_rail")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_default_model_state("powered=false,shape=north_south")
)
DEFERRED_PIPE.create_later(plant("minecraft:allium"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:amethyst_block"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:amethyst_cluster")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_default_model_state("facing=up")
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:ancient_debris"))

stone_like("andesite")

DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:azalea_leaves")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:azalea_leaves_flowers")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(plant("minecraft:azure_bluet"))
DEFERRED_PIPE.create_later(
    plant("minecraft:bamboo").set_default_model_state("age=0,leaves=small")
)
DEFERRED_PIPE.create_later(plant("minecraft:bamboo_sapling"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:barrier")
    .set_break_able_flag(False)
    .set_all_side_solid(False)
    .set_solid(False)
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:basalt").set_log())
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:beacon")
    .set_all_side_solid(False)
    .set_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:bedrock").set_break_able_flag(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:beehive")
    .set_default_model_state("facing=east,honey_level=3")
    .set_strength(0.6)
)
DEFERRED_PIPE.create_later(
    plant("minecraft:beetroots").set_default_model_state("age=2")
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:bee_nest")
    .set_default_model_state("facing=east,honey_level=2")
    .set_strength(0.3)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:bell")
    .set_default_model_state("attachment=ceiling,facing=north")
    .set_all_side_solid(False)
    .set_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:big_dripleaf")
    .set_default_model_state("facing=east,tilt=none")
    .set_all_side_solid(False)
    .set_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:big_dripleaf_stem")
    .set_default_model_state("facing=south")
    .set_all_side_solid(False)
    .set_solid(False)
)
wood("birch")
stone_like("blackstone", existing_fence=False)
colored("black")
colored("blue")
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:blue_ice"))
DEFERRED_PIPE.create_later(plant("minecraft:blue_orchid"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:bone_block").set_log())
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:bookshelf"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:brewing_stand")
    .set_default_model_state("has_bottle_0=false,has_bottle_1=false,has_bottle_2=false")
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like("bricks", existing_slab=True, existing_wall=True, existing_stairs=True)
colored("brown")
DEFERRED_PIPE.create_later(plant("minecraft:brown_mushroom"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:brown_mushroom_block")
    .set_default_model_state(
        "up=false,down=false,north=false,east=false,south=false,west=false"
    )
)
# todo: bubble column
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:budding_amethyst"))
DEFERRED_PIPE.create_later(plant("minecraft:cactus"))
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:cake").set_default_model_state("bites=5")
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:calcite"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:campfire")
    .set_default_model_state("facing=west,lit=true")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:candle")
    .set_default_model_state("candles=2,lit=true")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:candle_cake")
    .set_default_model_state("lit=true")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(plant("minecraft:carrots").set_default_model_state("age=3"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:cartography_table"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:carved_pumpkin").set_default_model_state("facing=south"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cauldron")
    .set_solid(False)
    .set_all_side_solid(False)
)
# todo: cave air
DEFERRED_PIPE.create_later(plant("minecraft:cave_vines").set_default_model_state("berries=false"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:chain")
    .set_log()
    .set_solid(False)
    .set_all_side_solid(False)
)
# todo: chain command block


# All blocks, by blockstate
"""
chiseled_deepslate
chiseled_grimstone
chiseled_nether_bricks
chiseled_polished_blackstone
chiseled_quartz_block
chiseled_red_sandstone
chiseled_sandstone
chiseled_stone_bricks
chorus_flower
chorus_plant
clay
coal_block
coal_ore
coarse_dirt
cobbled_deepslate
cobbled_deepslate_slab
cobbled_deepslate_stairs
cobbled_deepslate_wall
cobblestone
cobblestone_slab
cobblestone_stairs
cobblestone_wall
cobweb
cocoa
command_block
comparator
composter
conduit
copper_block
copper_ore
cornflower
cracked_deepslate_bricks
cracked_deepslate_tiles
cracked_nether_bricks
cracked_polished_blackstone_bricks
cracked_stone_bricks
crafting_table
creeper_head
creeper_wall_head
crimson_button
crimson_door
crimson_fence
crimson_fence_gate
crimson_fungus
crimson_hyphae
crimson_nylium
crimson_planks
crimson_pressure_plate
crimson_roots
crimson_sign
crimson_slab
crimson_stairs
crimson_stem
crimson_trapdoor
crimson_wall_sign
crying_obsidian
cut_copper
cut_copper_slab
cut_copper_stairs
cut_red_sandstone
cut_red_sandstone_slab
cut_sandstone
cut_sandstone_slab
cyan_banner
cyan_bed
cyan_candle
cyan_candle_cake
cyan_carpet
cyan_concrete
cyan_concrete_powder
cyan_glazed_terracotta
cyan_shulker_box
cyan_stained_glass
cyan_stained_glass_pane
cyan_terracotta
cyan_wall_banner
cyan_wool
dandelion
dark_oak_button
dark_oak_door
dark_oak_fence
dark_oak_fence_gate
dark_oak_leaves
dark_oak_log
dark_oak_planks
dark_oak_pressure_plate
dark_oak_sapling
dark_oak_sign
dark_oak_slab
dark_oak_stairs
dark_oak_trapdoor
dark_oak_wall_sign
dark_oak_wood
dark_prismarine
dark_prismarine_slab
dark_prismarine_stairs
daylight_detector
dead_brain_coral
dead_brain_coral_block
dead_brain_coral_fan
dead_brain_coral_wall_fan
dead_bubble_coral
dead_bubble_coral_block
dead_bubble_coral_fan
dead_bubble_coral_wall_fan
dead_bush
dead_fire_coral
dead_fire_coral_block
dead_fire_coral_fan
dead_fire_coral_wall_fan
dead_horn_coral
dead_horn_coral_block
dead_horn_coral_fan
dead_horn_coral_wall_fan
dead_tube_coral
dead_tube_coral_block
dead_tube_coral_fan
dead_tube_coral_wall_fan
deepslate
deepslate_bricks
deepslate_brick_slab
deepslate_brick_stairs
deepslate_brick_wall
deepslate_coal_ore
deepslate_copper_ore
deepslate_diamond_ore
deepslate_emerald_ore
deepslate_gold_ore
deepslate_iron_ore
deepslate_lapis_ore
deepslate_redstone_ore
deepslate_tiles
deepslate_tile_slab
deepslate_tile_stairs
deepslate_tile_wall
detector_rail
diamond_block
diamond_ore
diorite
diorite_slab
diorite_stairs
diorite_wall
dirt
dirt_path
dispenser
dragon_egg
dragon_head
dragon_wall_head
dried_kelp_block
dripstone_block
dropper
emerald_block
emerald_ore
enchanting_table
ender_chest
end_gateway
end_portal
end_portal_frame
end_rod
end_stone
end_stone_bricks
end_stone_brick_slab
end_stone_brick_stairs
end_stone_brick_wall
exposed_copper
exposed_cut_copper
exposed_cut_copper_slab
exposed_cut_copper_stairs
farmland
fern
fire
fire_coral
fire_coral_block
fire_coral_fan
fire_coral_wall_fan
fletching_table
flowering_azalea
flower_pot
frosted_ice
furnace
gilded_blackstone
glass
glass_pane
glowstone
glow_item_frame
glow_lichen
gold_block
gold_ore
granite
granite_slab
granite_stairs
granite_wall
grass
grass_block
gravel
gray_banner
gray_bed
gray_candle
gray_candle_cake
gray_carpet
gray_concrete
gray_concrete_powder
gray_glazed_terracotta
gray_shulker_box
gray_stained_glass
gray_stained_glass_pane
gray_terracotta
gray_wall_banner
gray_wool
green_banner
green_bed
green_candle
green_candle_cake
green_carpet
green_concrete
green_concrete_powder
green_glazed_terracotta
green_shulker_box
green_stained_glass
green_stained_glass_pane
green_terracotta
green_wall_banner
green_wool
grimstone
grimstone_bricks
grimstone_brick_slab
grimstone_brick_stairs
grimstone_brick_wall
grimstone_slab
grimstone_stairs
grimstone_tiles
grimstone_tile_slab
grimstone_tile_stairs
grimstone_tile_wall
grimstone_wall
grindstone
hanging_roots
hay_block
heavy_weighted_pressure_plate
honeycomb_block
honey_block
hopper
horn_coral
horn_coral_block
horn_coral_fan
horn_coral_wall_fan
ice
infested_chiseled_stone_bricks
infested_cobblestone
infested_cracked_stone_bricks
infested_deepslate
infested_mossy_stone_bricks
infested_stone
infested_stone_bricks
iron_bars
iron_block
iron_door
iron_ore
iron_trapdoor
item_frame
jack_o_lantern
jigsaw
jukebox
jungle_button
jungle_door
jungle_fence
jungle_fence_gate
jungle_leaves
jungle_log
jungle_planks
jungle_pressure_plate
jungle_sapling
jungle_sign
jungle_slab
jungle_stairs
jungle_trapdoor
jungle_wall_sign
jungle_wood
kelp
kelp_plant
ladder
lantern
lapis_block
lapis_ore
large_amethyst_bud
large_fern
lava
lava_cauldron
lectern
lever
light
lightning_rod
light_blue_banner
light_blue_bed
light_blue_candle
light_blue_candle_cake
light_blue_carpet
light_blue_concrete
light_blue_concrete_powder
light_blue_glazed_terracotta
light_blue_shulker_box
light_blue_stained_glass
light_blue_stained_glass_pane
light_blue_terracotta
light_blue_wall_banner
light_blue_wool
light_gray_banner
light_gray_bed
light_gray_candle
light_gray_candle_cake
light_gray_carpet
light_gray_concrete
light_gray_concrete_powder
light_gray_glazed_terracotta
light_gray_shulker_box
light_gray_stained_glass
light_gray_stained_glass_pane
light_gray_terracotta
light_gray_wall_banner
light_gray_wool
light_weighted_pressure_plate
lilac
lily_of_the_valley
lily_pad
lime_banner
lime_bed
lime_candle
lime_candle_cake
lime_carpet
lime_concrete
lime_concrete_powder
lime_glazed_terracotta
lime_shulker_box
lime_stained_glass
lime_stained_glass_pane
lime_terracotta
lime_wall_banner
lime_wool
lodestone
loom
magenta_banner
magenta_bed
magenta_candle
magenta_candle_cake
magenta_carpet
magenta_concrete
magenta_concrete_powder
magenta_glazed_terracotta
magenta_shulker_box
magenta_stained_glass
magenta_stained_glass_pane
magenta_terracotta
magenta_wall_banner
magenta_wool
magma_block
medium_amethyst_bud
melon
melon_stem
mossy_cobblestone
mossy_cobblestone_slab
mossy_cobblestone_stairs
mossy_cobblestone_wall
mossy_stone_bricks
mossy_stone_brick_slab
mossy_stone_brick_stairs
mossy_stone_brick_wall
moss_block
moss_carpet
moving_piston
mushroom_stem
mycelium
netherite_block
netherrack
nether_bricks
nether_brick_fence
nether_brick_slab
nether_brick_stairs
nether_brick_wall
nether_gold_ore
nether_portal
nether_quartz_ore
nether_sprouts
nether_wart
nether_wart_block
note_block
oak_button
oak_door
oak_fence
oak_fence_gate
oak_leaves
oak_log
oak_planks
oak_pressure_plate
oak_sapling
oak_sign
oak_slab
oak_stairs
oak_trapdoor
oak_wall_sign
oak_wood
observer
obsidian
orange_banner
orange_bed
orange_candle
orange_candle_cake
orange_carpet
orange_concrete
orange_concrete_powder
orange_glazed_terracotta
orange_shulker_box
orange_stained_glass
orange_stained_glass_pane
orange_terracotta
orange_tulip
orange_wall_banner
orange_wool
oxeye_daisy
oxidized_copper
oxidized_cut_copper
oxidized_cut_copper_slab
oxidized_cut_copper_stairs
packed_ice
peony
petrified_oak_slab
pink_banner
pink_bed
pink_candle
pink_candle_cake
pink_carpet
pink_concrete
pink_concrete_powder
pink_glazed_terracotta
pink_shulker_box
pink_stained_glass
pink_stained_glass_pane
pink_terracotta
pink_tulip
pink_wall_banner
pink_wool
piston
piston_head
player_head
player_wall_head
podzol
pointed_dripstone
polished_andesite
polished_andesite_slab
polished_andesite_stairs
polished_basalt
polished_blackstone
polished_blackstone_bricks
polished_blackstone_brick_slab
polished_blackstone_brick_stairs
polished_blackstone_brick_wall
polished_blackstone_button
polished_blackstone_pressure_plate
polished_blackstone_slab
polished_blackstone_stairs
polished_blackstone_wall
polished_deepslate
polished_deepslate_slab
polished_deepslate_stairs
polished_deepslate_wall
polished_diorite
polished_diorite_slab
polished_diorite_stairs
polished_granite
polished_granite_slab
polished_granite_stairs
polished_grimstone
polished_grimstone_slab
polished_grimstone_stairs
polished_grimstone_wall
poppy
potatoes
potted_acacia_sapling
potted_allium
potted_azure_bluet
potted_bamboo
potted_birch_sapling
potted_blue_orchid
potted_brown_mushroom
potted_cactus
potted_cornflower
potted_crimson_fungus
potted_crimson_roots
potted_dandelion
potted_dark_oak_sapling
potted_dead_bush
potted_fern
potted_jungle_sapling
potted_lily_of_the_valley
potted_oak_sapling
potted_orange_tulip
potted_oxeye_daisy
potted_pink_tulip
potted_poppy
potted_red_mushroom
potted_red_tulip
potted_spruce_sapling
potted_warped_fungus
potted_warped_roots
potted_white_tulip
potted_wither_rose
powder_snow
powder_snow_cauldron
powered_rail
prismarine
prismarine_bricks
prismarine_brick_slab
prismarine_brick_stairs
prismarine_slab
prismarine_stairs
prismarine_wall
pumpkin
pumpkin_stem
purple_banner
purple_bed
purple_candle
purple_candle_cake
purple_carpet
purple_concrete
purple_concrete_powder
purple_glazed_terracotta
purple_shulker_box
purple_stained_glass
purple_stained_glass_pane
purple_terracotta
purple_wall_banner
purple_wool
purpur_block
purpur_pillar
purpur_slab
purpur_stairs
quartz_block
quartz_bricks
quartz_pillar
quartz_slab
quartz_stairs
rail
raw_copper_block
raw_gold_block
raw_iron_block
redstone_block
redstone_lamp
redstone_ore
redstone_torch
redstone_wall_torch
redstone_wire
red_banner
red_bed
red_candle
red_candle_cake
red_carpet
red_concrete
red_concrete_powder
red_glazed_terracotta
red_mushroom
red_mushroom_block
red_nether_bricks
red_nether_brick_slab
red_nether_brick_stairs
red_nether_brick_wall
red_sand
red_sandstone
red_sandstone_slab
red_sandstone_stairs
red_sandstone_wall
red_shulker_box
red_stained_glass
red_stained_glass_pane
red_terracotta
red_tulip
red_wall_banner
red_wool
repeater
repeating_command_block
respawn_anchor
rooted_dirt
rose_bush
sand
sandstone
sandstone_slab
sandstone_stairs
sandstone_wall
scaffolding
sculk_sensor
seagrass
sea_lantern
sea_pickle
shroomlight
shulker_box
skeleton_skull
skeleton_wall_skull
slime_block
small_amethyst_bud
small_dripleaf
smithing_table
smoker
smooth_basalt
smooth_quartz
smooth_quartz_slab
smooth_quartz_stairs
smooth_red_sandstone
smooth_red_sandstone_slab
smooth_red_sandstone_stairs
smooth_sandstone
smooth_sandstone_slab
smooth_sandstone_stairs
smooth_stone
smooth_stone_slab
snow
snow_block
soul_campfire
soul_fire
soul_lantern
soul_sand
soul_soil
soul_torch
soul_wall_torch
spawner
sponge
spore_blossom
spruce_button
spruce_door
spruce_fence
spruce_fence_gate
spruce_leaves
spruce_log
spruce_planks
spruce_pressure_plate
spruce_sapling
spruce_sign
spruce_slab
spruce_stairs
spruce_trapdoor
spruce_wall_sign
spruce_wood
sticky_piston
stone
stonecutter
stone_bricks
stone_brick_slab
stone_brick_stairs
stone_brick_wall
stone_button
stone_pressure_plate
stone_slab
stone_stairs
stripped_acacia_log
stripped_acacia_wood
stripped_birch_log
stripped_birch_wood
stripped_crimson_hyphae
stripped_crimson_stem
stripped_dark_oak_log
stripped_dark_oak_wood
stripped_jungle_log
stripped_jungle_wood
stripped_oak_log
stripped_oak_wood
stripped_spruce_log
stripped_spruce_wood
stripped_warped_hyphae
stripped_warped_stem
structure_block
structure_void
sugar_cane
sunflower
sweet_berry_bush
tall_grass
tall_seagrass
target
terracotta
tinted_glass
tnt
torch
trapped_chest
tripwire
tripwire_hook
tube_coral
tube_coral_block
tube_coral_fan
tube_coral_wall_fan
tuff
turtle_egg
twisting_vines
twisting_vines_plant
vine
void_air
wall_torch
warped_button
warped_door
warped_fence
warped_fence_gate
warped_fungus
warped_hyphae
warped_nylium
warped_planks
warped_pressure_plate
warped_roots
warped_sign
warped_slab
warped_stairs
warped_stem
warped_trapdoor
warped_wall_sign
warped_wart_block
water
water_cauldron
waxed_copper_block
waxed_cut_copper
waxed_cut_copper_slab
waxed_cut_copper_stairs
waxed_exposed_copper
waxed_exposed_cut_copper
waxed_exposed_cut_copper_slab
waxed_exposed_cut_copper_stairs
waxed_oxidized_copper
waxed_oxidized_cut_copper
waxed_oxidized_cut_copper_slab
waxed_oxidized_cut_copper_stairs
waxed_weathered_copper
waxed_weathered_cut_copper
waxed_weathered_cut_copper_slab
waxed_weathered_cut_copper_stairs
weathered_copper
weathered_cut_copper
weathered_cut_copper_slab
weathered_cut_copper_stairs
weeping_vines
weeping_vines_plant
wet_sponge
wheat
white_banner
white_bed
white_candle
white_candle_cake
white_carpet
white_concrete
white_concrete_powder
white_glazed_terracotta
white_shulker_box
white_stained_glass
white_stained_glass_pane
white_terracotta
white_tulip
white_wall_banner
white_wool
wither_rose
wither_skeleton_skull
wither_skeleton_wall_skull
yellow_banner
yellow_bed
yellow_candle
yellow_candle_cake
yellow_carpet
yellow_concrete
yellow_concrete_powder
yellow_glazed_terracotta
yellow_shulker_box
yellow_stained_glass
yellow_stained_glass_pane
yellow_terracotta
yellow_wall_banner
yellow_wool
zombie_head
zombie_wall_head
"""
