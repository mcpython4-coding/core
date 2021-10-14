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
    return BlockFactory().set_name(name).set_strength(0).set_flower_like()


def large_plant(name: str):
    return plant(name).set_default_model_state("half=lower")


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
        .set_button()
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
    consumer=lambda _, __: None,
):
    fname = name.removesuffix("s")
    instance = CombinedFactoryInstance(
        f"minecraft:{name}",
        f"minecraft:block/{name}" if texture is None else texture,
        deferred_registry=DEFERRED_PIPE,
    )

    if existing_full:
        obj = BlockFactory().set_name(f"minecraft:{name}")
        consumer(None, obj)
        DEFERRED_PIPE.create_later(obj)
    else:
        instance.create_full_block(block_factory_consumer=consumer)

    if existing_slab:
        obj = BlockFactory().set_name(f"minecraft:{fname}_slab").set_slab()
        consumer(None, obj)
        DEFERRED_PIPE.create_later(obj)
    else:
        instance.create_slab_block(
            f"minecraft:{fname}_slab", block_factory_consumer=consumer
        )

    if existing_wall:
        obj = BlockFactory().set_name(f"minecraft:{fname}_wall").set_wall()
        consumer(None, obj)
        DEFERRED_PIPE.create_later(obj)
    else:
        instance.create_wall(f"minecraft:{fname}_wall", block_factory_consumer=consumer)

    if existing_stairs:
        obj = (
            BlockFactory()
            .set_name(f"minecraft:{fname}_stairs")
            .set_default_model_state("facing=east,half=bottom,shape=inner_left")
            .set_solid(False)
            .set_all_side_solid(False)
        )
        consumer(None, obj)
        DEFERRED_PIPE.create_later(obj)
    else:
        pass  # todo: implement

    if existing_fence:
        obj = BlockFactory().set_name(f"minecraft:{fname}_fence").set_fence()
        consumer(None, obj)
        DEFERRED_PIPE.create_later(obj)
    else:
        instance.create_fence(
            f"minecraft:{fname}_fence", block_factory_consumer=consumer
        )


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

    stone_like(
        f"{name}_concrete",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
    )

    DEFERRED_PIPE.create_later(
        BlockFactory().set_name(f"minecraft:{name}_concrete_powder").set_fall_able()
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_glazed_terracotta")
        .set_default_model_state("facing=east")
    )

    stone_like(
        f"{name}_stained_glass",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
    )

    # todo: glass pane

    DEFERRED_PIPE.create_later(BlockFactory().set_name(f"minecraft:{name}_terracotta"))

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_wall_banner")
        .set_solid(False)
        .set_all_side_solid(False)
    )

    stone_like(f"{name}_wool")


# Technical blocks
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:barrier")
    .set_break_able_flag(False)
    .set_all_side_solid(False)
    .set_solid(False)
)

# Wood based
wood("acacia")

# Stone based
stone_like("andesite")
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:basalt").set_log())

# Value blocks
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:ancient_debris"))

DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:amethyst_block"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:amethyst_cluster")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_default_model_state("facing=up")
)

# Nature blocks
DEFERRED_PIPE.create_later(plant("minecraft:allium"))
DEFERRED_PIPE.create_later(plant("minecraft:azure_bluet"))
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
DEFERRED_PIPE.create_later(
    plant("minecraft:bamboo").set_default_model_state("age=0,leaves=small")
)
DEFERRED_PIPE.create_later(plant("minecraft:bamboo_sapling"))

# Unsorted

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
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:carved_pumpkin")
    .set_default_model_state("facing=south")
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cauldron")
    .set_solid(False)
    .set_all_side_solid(False)
)
# todo: cave air
DEFERRED_PIPE.create_later(
    plant("minecraft:cave_vines").set_default_model_state("berries=false")
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:chain")
    .set_log()
    .set_solid(False)
    .set_all_side_solid(False)
)
# todo: chain command block
stone_like(
    "chiseled_deepslate",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "chiseled_polished_blackstone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "chiseled_quartz_block",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "chiseled_red_sandstone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "chiseled_sandstone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "chiseled_stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
DEFERRED_PIPE.create_later(
    plant("minecraft:chorus_flower").set_default_model_state("age=3")
)
DEFERRED_PIPE.create_later(
    plant("minecraft:chorus_plant").set_default_model_state(
        "north=false,south=false,east=false,west=false,up=false,down=false"
    )
)
stone_like("clay", existing_slab=False, existing_stairs=False, existing_wall=False)
stone_like(
    "coal_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:coal_ore"))
stone_like(
    "coarse_dirt", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "cobbled_deepslate", existing_slab=True, existing_stairs=True, existing_wall=True
)
stone_like("cobblestone", existing_slab=True, existing_stairs=True, existing_wall=True)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cobweb")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cocoa")
    .set_default_model_state("age=2,facing=east")
    .set_solid(False)
    .set_all_side_solid(False)
)
# todo: command block
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:comparator")
    .set_default_model_state("facing=north,mode=compare,powered=true")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:composter")
    .set_default_model_state("level=2")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:conduit")
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like(
    "copper_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:copper_ore"))
DEFERRED_PIPE.create_later(plant("cornflower"))
stone_like(
    "cracked_deepslate_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "cracked_deepslate_tiles",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "cracked_nether_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "cracked_polished_blackstone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "cracked_stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
# todo: creeper head & wall head
wood("crimson", normal=False)
stone_like(
    "crying_obsidian", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like("cut_copper", existing_slab=True, existing_stairs=True, existing_wall=False)
stone_like(
    "cut_red_sandstone", existing_slab=True, existing_stairs=False, existing_wall=False
)
stone_like(
    "cut_sandstone", existing_slab=True, existing_stairs=False, existing_wall=False
)
colored("cyan")
DEFERRED_PIPE.create_later(plant("dandelion"))
wood("dark_oak")
stone_like(
    "dark_prismarine", existing_slab=True, existing_stairs=True, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:daylight_detector")
    .set_default_model_state("inverted=false")
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like("deepslate", existing_slab=False, existing_stairs=False, existing_wall=False)
stone_like(
    "deepslate_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
)
stone_like(
    "deepslate_tiles", existing_slab=True, existing_stairs=True, existing_wall=True
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_coal_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_copper_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_diamond_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_emerald_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_gold_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_iron_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_lapis_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate_redstone_ore"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:detector_rail")
    .set_default_model_state("powered=false,shape=ascending_south")
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like(
    "diamond_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:diamond_ore"))
stone_like("diorite", existing_slab=True, existing_stairs=True, existing_wall=True)
stone_like("dirt", existing_slab=False, existing_stairs=False, existing_wall=False)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:dirt_path")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:dispenser").set_all_direction_orientable()
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:dragon_egg")
    .set_solid(False)
    .set_all_side_solid(False)
)
# todo: dragon head
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:dried_kelp_block"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:dripstone_block"))
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:dropper").set_all_direction_orientable()
)
stone_like(
    "emerald_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:emerald_ore"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:enchanting_table")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:end_gateway")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:end_portal")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:end_portal_frame")
    .set_default_model_state("eye=false,facing=south")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:end_rod")
    .set_all_direction_orientable()
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like("end_stone", existing_slab=False, existing_stairs=False, existing_wall=False)
stone_like(
    "end_stone_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
)
stone_like(
    "exposed_copper", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "exposed_cut_copper", existing_slab=True, existing_stairs=True, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:farmland")
    .set_default_model_state("moisture=0")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(plant("minecraft:fern"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:fire")
    .set_default_model_state("north=false,east=false,west=false,south=false")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:fletching_table"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:flowering_azalea")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:flower_pot")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:frosted_ice")
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like(
    "gilded_blackstone", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "glass",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
)
# todo: glass pane
stone_like("glowstone", existing_slab=False, existing_stairs=False, existing_wall=False)
# todo: glow item frame and glow lichen
stone_like(
    "gold_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:gold_ore"))
stone_like("granite", existing_slab=True, existing_stairs=True, existing_wall=True)
DEFERRED_PIPE.create_later(plant("grass"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:gravel").set_fall_able())
colored("gray")
colored("green")
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:grindstone")
    .set_all_side_solid(False)
    .set_solid(False)
    .set_default_model_state("face=ceiling,facing=north")
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:hanging_roots"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:hay_block").set_log())
# todo: heavy_weighted_pressure_plate
stone_like(
    "honeycomb_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:honey_block")
    .set_all_side_solid(False)
    .set_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:hopper")
    .set_all_side_solid(False)
    .set_solid(False)
    .set_default_model_state("facing=east")
)  # todo: create real block behaviour
stone_like("ice")  # todo: melting

# todo: add infection
stone_like(
    "infested_chiseled_stone_bricks",
    texture="minecraft:block/chiseled_stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "infested_cobblestone",
    texture="minecraft:block/cobblestone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "infested_cracked_stone_bricks",
    texture="minecraft:block/cracked_stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "infested_deepslate",
    texture="minecraft:block/deepslate",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "infested_mossy_stone_bricks",
    texture="minecraft:block/mossy_stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "infested_stone",
    texture="minecraft:block/stone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)
stone_like(
    "infested_stone_bricks",
    texture="minecraft:block/stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
)

DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:iron_bars").set_fence())
stone_like("iron_block")
# todo: iron door
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:iron_ore"))
# todo: iron trapdoor, item frame
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:jack_o_lantern").set_horizontal_orientable()
)
# todo: jigsaw block
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:jukebox"))
wood("jungle")
DEFERRED_PIPE.create_later(plant("minecraft:kelp"))
DEFERRED_PIPE.create_later(plant("minecraft:kelp_plant"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:ladder")
    .set_horizontal_orientable()
    .set_all_side_solid(False)
    .set_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:lantern")
    .set_default_model_state("hanging=false")
    .set_all_side_solid(False)
    .set_solid(False)
)
stone_like(
    "lapis_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:lapis_ore"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:large_amethyst_bud")
    .set_all_direction_orientable()
)
DEFERRED_PIPE.create_later(large_plant("minecraft:large_fern"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:lava_cauldron")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:lectern")
    .set_horizontal_orientable()
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:lever")
    .set_default_model_state("face=ceiling,facing=north,powered=false")
    .set_all_side_solid(False)
    .set_solid(False)
)
# todo: light
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:lightning_rod")
    .set_default_model_state("facing=west,powered=false")
    .set_all_side_solid(False)
    .set_solid(False)
)
colored("light_blue")
colored("light_gray")
# todo: light_weighted_pressure_plate
DEFERRED_PIPE.create_later(large_plant("minecraft:lilac"))
DEFERRED_PIPE.create_later(plant("minecraft:lily_of_the_valley"))
DEFERRED_PIPE.create_later(plant("minecraft:lily_pad").set_horizontal_orientable())
colored("lime")
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:lodestone"))
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:loom").set_horizontal_orientable()
)
colored("magenta")
stone_like(
    "magma_block",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    texture="minecraft:block/magma",
)

# All remaining blocks, by blockstate
"""
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
