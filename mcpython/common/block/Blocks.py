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
import typing

from mcpython import shared
from mcpython.common.event.DeferredRegistryHelper import DeferredRegistry
from mcpython.common.factory.BlockFactory import BlockFactory
from mcpython.common.factory.combined.simple import CombinedFactoryInstance

# Missing:
# air
# attached_melon_stem
# attached_pumpkin_stem
from mcpython.util.enums import ToolType

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
        .set_button()
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_door")
        .set_default_model_state("facing=east,half=upper,hinge=left,open=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_fence")
        .set_fence()
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_fence_gate")
        .set_fence_gate()
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )

    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_planks")
        .set_strength(2)
        .set_assigned_tools(ToolType.AXE)
    )
    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_pressure_plate")
        .set_default_model_state("powered=false")
        .set_solid(False)
        .set_all_side_solid(False)
        .set_strength(0.5)
        .set_assigned_tools(ToolType.AXE)
    )
    DEFERRED_PIPE.create_later(
        BlockFactory()
        .set_name(f"minecraft:{name}_slab")
        .set_slab()
        .set_strength(2)
        .set_assigned_tools(ToolType.AXE)
    )

    if normal:
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:{name}_leaves")
            .set_solid(False)
            .set_all_side_solid(False)
            .set_strength(0.2)
            .set_assigned_tools(ToolType.SHEAR)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:{name}_log")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_log")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory().set_name(f"minecraft:{name}_wood").set_log().set_strength(2)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_wood")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        DEFERRED_PIPE.create_later(plant(f"minecraft:{name}_sapling"))
        DEFERRED_PIPE.create_later(plant(f"minecraft:potted_{name}_sapling"))
    else:
        DEFERRED_PIPE.create_later(
            BlockFactory().set_name(f"minecraft:{name}_stem").set_log().set_strength(2)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_stem")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:{name}_hyphae")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:stripped_{name}_hyphae")
            .set_log()
            .set_strength(2)
            .set_assigned_tools(ToolType.AXE)
        )

    CombinedFactoryInstance(
        f"minecraft:{name}_wall",
        f"minecraft:block/{name}_planks",
        block_phase="stage:block:load_late",
    ).create_wall(
        suffix="_wall",
        block_factory_consumer=lambda _, instance: instance.set_strength(
            0.5
        ).set_assigned_tools(ToolType.AXE),
    )

    # todo: signs, stairs


def stone_like(
    name: str,
    existing_full=True,
    existing_slab=True,
    existing_wall=True,
    existing_stairs=True,
    existing_fence=False,
    existing_button=False,
    existing_pressure_plate=False,
    texture=None,
    consumer=lambda _, __: None,
    strength: typing.Union[float, typing.Tuple[float, float]] = 2,
    tool=ToolType.PICKAXE,
):
    consumer = (
        lambda _, inst: tool
        == inst.set_strength(strength).set_assigned_tools((tool,))
        == consumer(_, inst)
    )

    fname = name.removesuffix("s")
    instance = CombinedFactoryInstance(
        f"minecraft:{name}",
        f"minecraft:block/{name}" if texture is None else texture,
        block_phase="stage:block:load_late",
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

    if existing_button:
        DEFERRED_PIPE.create_later(
            BlockFactory()
            .set_name(f"minecraft:{fname}_button")
            .set_button()
            .set_solid(False)
            .set_all_side_solid(False)
        )
    else:
        # instance.create_button_block(f"minecraft:{fname}_button", block_factory_consumer=consumer)
        # todo: implement
        pass


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

    stone_like(
        f"{name}_wool",
        existing_slab=False,
        existing_stairs=False,
        existing_wall=False,
        consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
    )


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
stone_like("andesite", strength=(1.5, 6))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:basalt")
    .set_log()
    .set_strength(1.25, 4.2)
    .set_assigned_tools(ToolType.PICKAXE)
)

# Value blocks
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:ancient_debris")
    .set_assigned_tools(ToolType.PICKAXE)
    .set_strength(30, 1200)
)

DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:amethyst_block")
    .set_assigned_tools(ToolType.PICKAXE)
    .set_strength(1.5)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:amethyst_cluster")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_default_model_state("facing=up")
    .set_assigned_tools(ToolType.PICKAXE)
    .set_strength(1.5)
)

# Nature blocks
DEFERRED_PIPE.create_later(plant("minecraft:allium"))
DEFERRED_PIPE.create_later(plant("minecraft:azure_bluet"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:azalea_leaves")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_assigned_tools(ToolType.SHEAR)
    .set_strength(0.2)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:flowering_azalea_leaves")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_assigned_tools(ToolType.SHEAR)
    .set_strength(0.2)
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
    .set_strength(3)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:bedrock")
    .set_break_able_flag(False)
    .set_strength(-1, 3600000)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:beehive")
    .set_default_model_state("facing=east,honey_level=3")
    .set_strength(0.6)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    plant("minecraft:beetroots").set_default_model_state("age=2")
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:bee_nest")
    .set_default_model_state("facing=east,honey_level=2")
    .set_strength(0.3)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:bell")
    .set_default_model_state("attachment=ceiling,facing=north")
    .set_all_side_solid(False)
    .set_solid(False)
    .set_strength(5)
    .set_assigned_tools(ToolType.PICKAXE)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:big_dripleaf")
    .set_default_model_state("facing=east,tilt=none")
    .set_all_side_solid(False)
    .set_solid(False)
    .set_strength(0.1)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:big_dripleaf_stem")
    .set_default_model_state("facing=south")
    .set_all_side_solid(False)
    .set_solid(False)
    .set_strength(0.1)
    .set_assigned_tools(ToolType.AXE)
)
wood("birch")
stone_like("blackstone", existing_fence=False, strength=6)
colored("black")
colored("blue")
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:blue_ice")
    .set_strength(2.8)
    .set_assigned_tools(ToolType.PICKAXE)
)
DEFERRED_PIPE.create_later(plant("minecraft:blue_orchid"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:bone_block")
    .set_log()
    .set_strength(2.0)
    .set_assigned_tools(ToolType.PICKAXE)
    .set_minimum_tool_level(1)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:bookshelf")
    .set_strength(1.5)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:brewing_stand")
    .set_default_model_state("has_bottle_0=false,has_bottle_1=false,has_bottle_2=false")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(0.5)
    .set_assigned_tools(ToolType.PICKAXE)
    .set_minimum_tool_level(1)
)
stone_like(
    "bricks",
    existing_slab=True,
    existing_wall=True,
    existing_stairs=True,
    strength=(6, 2),
)
colored("brown")
DEFERRED_PIPE.create_later(plant("minecraft:brown_mushroom"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:brown_mushroom_block")
    .set_default_model_state(
        "up=false,down=false,north=false,east=false,south=false,west=false"
    )
    .set_strength(0.2)
    .set_assigned_tools(ToolType.AXE)
)
# todo: bubble column
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:budding_amethyst")
    .set_strength(1.5)
    .set_assigned_tools(ToolType.PICKAXE)
)
DEFERRED_PIPE.create_later(plant("minecraft:cactus").set_strength(0.4))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cake")
    .set_default_model_state("bites=5")
    .set_strength(0.5)
)
stone_like(
    "calcite",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=0.75,
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:campfire")
    .set_default_model_state("facing=west,lit=true")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(2)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:candle")
    .set_default_model_state("candles=2,lit=true")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(0.1)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:candle_cake")
    .set_default_model_state("lit=true")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(0.5)
)
DEFERRED_PIPE.create_later(plant("minecraft:carrots").set_default_model_state("age=3"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cartography_table")
    .set_strength(2.5)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:carved_pumpkin")
    .set_horizontal_orientable()
    .set_strength(1)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cauldron")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(2)
    .set_assigned_tools(ToolType.PICKAXE)
    .set_minimum_tool_level(1)
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
    .set_strength(5, 6)
    .set_assigned_tools(ToolType.PICKAXE)
    .set_minimum_tool_level(1)
)
# todo: chain command block
stone_like(
    "chiseled_deepslate",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(3, 6),
    tool=ToolType.PICKAXE,
)
stone_like(
    "chiseled_polished_blackstone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(1.5, 6),
    tool=ToolType.PICKAXE,
)
stone_like(
    "chiseled_quartz_block",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=0.8,
    tool=ToolType.PICKAXE,
)
stone_like(
    "chiseled_red_sandstone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=0.8,
    tool=ToolType.PICKAXE,
)
stone_like(
    "chiseled_sandstone",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=0.8,
    tool=ToolType.PICKAXE,
)
stone_like(
    "chiseled_stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(1.5, 6),
    tool=ToolType.PICKAXE,
)
DEFERRED_PIPE.create_later(
    plant("minecraft:chorus_flower")
    .set_default_model_state("age=3")
    .set_strength(0.4)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    plant("minecraft:chorus_plant")
    .set_default_model_state(
        "north=false,south=false,east=false,west=false,up=false,down=false"
    )
    .set_strength(0.4)
    .set_assigned_tools(ToolType.AXE)
)
stone_like(
    "clay",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=0.6,
    tool=ToolType.SHOVEL,
)
stone_like(
    "coal_block",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(5, 6),
    tool=ToolType.PICKAXE,
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:coal_ore")
    .set_strength(3)
    .set_assigned_tools(ToolType.PICKAXE)
    .set_minimum_tool_level(1)
)
stone_like(
    "coarse_dirt",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=0.5,
    tool=ToolType.SHOVEL,
)
stone_like(
    "cobbled_deepslate",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=True,
    strength=(3.5, 6),
    tool=ToolType.PICKAXE,
)
stone_like(
    "cobblestone",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=True,
    strength=(2, 6),
    tool=ToolType.PICKAXE,
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cobweb")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(4)
    .set_assigned_tools((ToolType.SHEAR, ToolType.SWORD))
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:cocoa")
    .set_default_model_state("age=2,facing=east")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(.2, 3)
    .set_assigned_tools((ToolType.AXE))
)
# todo: command block
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:comparator")
    .set_default_model_state("facing=north,mode=compare,powered=true")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(0)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:composter")
    .set_default_model_state("level=2")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(.6)
    .set_assigned_tools(ToolType.AXE)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:conduit")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_strength(3)
    .set_assigned_tools(ToolType.PICKAXE)
)
stone_like(
    "copper_block", existing_slab=False, existing_stairs=False, existing_wall=False, strength=(3, 6)
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:copper_ore").set_strength(3).set_assigned_tools(ToolType.PICKAXE).set_minimum_tool_level(2))
DEFERRED_PIPE.create_later(plant("cornflower"))
stone_like(
    "cracked_deepslate_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(3, 6),
)
stone_like(
    "cracked_deepslate_tiles",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(3, 6),
)
stone_like(
    "cracked_nether_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(2, 6),
)
stone_like(
    "cracked_polished_blackstone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(1.5, 6),
)
stone_like(
    "cracked_stone_bricks",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    strength=(1.5, 6),
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
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:deepslate").set_log())
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
    .set_default_model_state("age=1")
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
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:infested_deepslate").set_log()
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
DEFERRED_PIPE.create_later(plant("minecraft:lily_pad"))
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
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:medium_amethyst_bud")
    .set_all_direction_orientable()
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:melon"))
DEFERRED_PIPE.create_later(
    plant("minecraft:melon_stem").set_default_model_state("age=7")
)
stone_like(
    "mossy_cobblestone", existing_slab=True, existing_stairs=True, existing_wall=True
)
stone_like(
    "mossy_stone_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
)
stone_like(
    "moss_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:moss_carpet")
    .set_all_side_solid(False)
    .set_solid(False)
)
# todo: moving piston, mushroom stem
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:mycelium").set_default_model_state("snowy=false")
)
stone_like(
    "netherite_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "netherrack", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "nether_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:nether_gold_ore"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:nether_quartz_ore"))
DEFERRED_PIPE.create_later(plant("minecraft:nether_sprouts"))
DEFERRED_PIPE.create_later(
    plant("minecraft:nether_wart").set_default_model_state("age=2")
)
stone_like(
    "nether_wart_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:note_block"))
wood("oak")
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:observerer")
    .set_default_model_state("facing=north,powered=false")
)
stone_like("obsidian", existing_slab=False, existing_stairs=False, existing_wall=False)
colored("orange")
DEFERRED_PIPE.create_later(plant("minecraft:oxeye_daisy"))
stone_like(
    "oxidized_copper", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "oxidized_cut_copper", existing_slab=True, existing_stairs=True, existing_wall=False
)
stone_like(
    "packed_ice", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(large_plant("minecraft:peony"))
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:petrified_oak_slab").set_slab()
)
colored("pink")
DEFERRED_PIPE.create_later(plant("minecraft:pink_tulip"))
# todo: piston, piston head, player head, player wall head
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:podzol").set_default_model_state("snowy=false")
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:pointed_dripstone")
    .set_default_model_state("thickness=middle,vertical_direction=up")
)
stone_like(
    "polished_andesite", existing_slab=True, existing_stairs=True, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:polished_basalt").set_log()
)
stone_like(
    "polished_blackstone",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=True,
    existing_button=True,
    existing_pressure_plate=True,
)
stone_like(
    "polished_blackstone_bricks",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=True,
)
stone_like(
    "polished_deepslate", existing_slab=True, existing_stairs=True, existing_wall=True
)
stone_like(
    "polished_diorite", existing_slab=True, existing_stairs=True, existing_wall=False
)
stone_like(
    "polished_granite", existing_slab=True, existing_stairs=True, existing_wall=False
)
DEFERRED_PIPE.create_later(plant("minecraft:poppy"))
DEFERRED_PIPE.create_later(plant("minecraft:potatoes").set_default_model_state("age=4"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_allium"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_azure_bluet"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_bamboo"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_blue_orchid"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_brown_mushroom"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_cactus"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_cornflower"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_crimson_fungus"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_crimson_roots"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_dandelion"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_dead_bush"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_fern"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_lily_of_the_valley"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_orange_tulip"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_pink_tulip"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_oxeye_daisy"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_pink_tulip"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_poppy"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_red_mushroom"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_red_tulip"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_warped_fungus"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_warped_roots"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_white_tulip"))
DEFERRED_PIPE.create_later(plant("minecraft:potted_wither_rose"))
# todo: powder_snow
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:powder_snow_cauldron")
    .set_solid(False)
    .set_all_side_solid(False)
    .set_default_model_state("level=2")
)
stone_like("prismarine", existing_slab=True, existing_stairs=True, existing_wall=True)
stone_like(
    "prismarine_bricks", existing_slab=True, existing_stairs=True, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:pumpkin"))
DEFERRED_PIPE.create_later(
    plant("minecraft:pumpkin_stem").set_default_model_state("age=2")
)
colored("purple")
stone_like(
    "purpur_block", existing_slab=True, existing_stairs=True, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:purpur_pillar").set_log())
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:quartz_block"))
stone_like(
    "quartz_bricks", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:quartz_pillar").set_log())
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:quartz_slab").set_slab())
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:quartz_stairs")
    .set_default_model_state("facing=east,half=bottom,shape=inner_left")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:rail")
    .set_default_model_state("shape=east_west")
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like(
    "raw_copper_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "raw_gold_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "raw_iron_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "redstone_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:redstone_lamp")
    .set_default_model_state("lit=false")
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:redstone_ore"))
# todo: redstone torch & wall torch
colored("red")
DEFERRED_PIPE.create_later(plant("minecraft:red_mushroom"))
# todo: red mushroom_block
stone_like(
    "red_nether_bricks", existing_slab=True, existing_stairs=True, existing_wall=True
)
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:red_sand").set_fall_able()
)
stone_like(
    "red_sandstone", existing_slab=True, existing_stairs=True, existing_wall=True
)
DEFERRED_PIPE.create_later(plant("minecraft:red_tulip"))
# todo: repeater, repeating_command_block
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:respawn_anchor")
    .set_default_model_state("charges=2")
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:rooted_dirt"))
DEFERRED_PIPE.create_later(large_plant("minecraft:rose_bush"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:sand").set_fall_able())
stone_like("sandstone", existing_slab=True, existing_stairs=True, existing_wall=True)
# todo: scaffolding
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:sculk_sensor")
    .set_default_model_state("sculk_sensor_phase=inactive")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(plant("minecraft:seagrass"))
stone_like(
    "sea_lantern", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(
    plant("minecraft:sea_pickle").set_default_model_state("pickles=1,waterlogged=true")
)
stone_like(
    "shroomlight", existing_slab=False, existing_stairs=False, existing_wall=False
)
# todo: skeleton skull
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:slime_block")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:small_amethyst_bud")
    .set_all_direction_orientable()
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:small_dripleaf")
    .set_default_model_state("facing=north,half=upper")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:smithing_table"))
stone_like(
    "smooth_basalt", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "smooth_quartz",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    texture="minecraft:block/quartz_block_bottom",
)
stone_like(
    "smooth_red_sandstone",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    texture="minecraft:block/red_sandstone_top",
)
stone_like(
    "smooth_sandstone",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    texture="minecraft:block/sandstone_top",
)
stone_like(
    "smooth_stone", existing_slab=True, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:snow")
    .set_default_model_state("layers=7")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:snow_block"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:soul_campfire")
    .set_default_model_state("facing=west,lit=true")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:soul_fire")
    .set_default_model_state("north=false,east=false,west=false,south=false")
    .set_solid(False)
    .set_all_side_solid(False)
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:soul_lantern")
    .set_default_model_state("hanging=false")
    .set_all_side_solid(False)
    .set_solid(False)
)
stone_like("soul_sand", existing_slab=False, existing_stairs=False, existing_wall=False)
stone_like("soul_soil", existing_slab=False, existing_stairs=False, existing_wall=False)
# todo: soul torch, spawner
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:sponge"))
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:spore_blossom")
    .set_solid(False)
    .set_all_side_solid(False)
)
wood("spruce")
# todo: sticky piston
stone_like(
    "stone",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    existing_button=True,
    existing_pressure_plate=True,
)
DEFERRED_PIPE.create_later(
    BlockFactory().set_name("minecraft:stonecutter").set_horizontal_orientable()
)
stone_like("stone_bricks", existing_slab=True, existing_stairs=True, existing_wall=True)
# todo: structure block, structure void
DEFERRED_PIPE.create_later(plant("minecraft:sugar_cane"))
DEFERRED_PIPE.create_later(large_plant("minecraft:sunflower"))
DEFERRED_PIPE.create_later(
    plant("minecraft:sweet_berry_bush").set_default_model_state("age=2")
)
DEFERRED_PIPE.create_later(large_plant("minecraft:tall_grass"))
DEFERRED_PIPE.create_later(large_plant("minecraft:tall_seagrass"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:target"))
stone_like(
    "terracotta", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "tinted_glass",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    consumer=lambda _, factory: factory.set_solid(False).set_all_side_solid(False),
)
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:tnt"))
# todo: torch, tripwire, tripwire hook
stone_like("tuff", existing_slab=False, existing_stairs=False, existing_wall=False)
# todo: turtle egg, twisted vines, vine, void air
wood("warped", normal=False)
DEFERRED_PIPE.create_later(plant("minecraft:warped_fungus"))
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:warped_nylium"))
DEFERRED_PIPE.create_later(plant("minecraft:warped_roots"))
stone_like(
    "warped_wart_block", existing_slab=False, existing_stairs=False, existing_wall=False
)
DEFERRED_PIPE.create_later(
    BlockFactory()
    .set_name("minecraft:water_cauldron")
    .set_default_model_state("level=2")
    .set_solid(False)
    .set_all_side_solid(False)
)
stone_like(
    "waxed_copper_block",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    texture="minecraft:block/copper_block",
)
stone_like(
    "waxed_cut_copper",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    texture="minecraft:block/cut_copper",
)
stone_like(
    "waxed_exposed_copper",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    texture="minecraft:block/exposed_copper",
)
stone_like(
    "waxed_exposed_cut_copper",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    texture="minecraft:block/exposed_cut_copper",
)
stone_like(
    "waxed_oxidized_copper",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    texture="minecraft:block/oxidized_copper",
)
stone_like(
    "waxed_oxidized_cut_copper",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    texture="minecraft:block/oxidized_cut_copper",
)
stone_like(
    "waxed_weathered_copper",
    existing_slab=False,
    existing_stairs=False,
    existing_wall=False,
    texture="minecraft:block/weathered_copper",
)
stone_like(
    "waxed_weathered_cut_copper",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
    texture="minecraft:block/weathered_cut_copper",
)
stone_like(
    "weathered_copper", existing_slab=False, existing_stairs=False, existing_wall=False
)
stone_like(
    "weathered_cut_copper",
    existing_slab=True,
    existing_stairs=True,
    existing_wall=False,
)
# todo: weeping vines
DEFERRED_PIPE.create_later(BlockFactory().set_name("minecraft:wet_sponge"))
DEFERRED_PIPE.create_later(plant("minecraft:wheat").set_default_model_state("age=3"))
colored("white")
DEFERRED_PIPE.create_later(plant("minecraft:white_tulip"))
DEFERRED_PIPE.create_later(plant("minecraft:wither_rose"))
# todo: wither skeleton skull
colored("yellow")
# todo: zombie head
