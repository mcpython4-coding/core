"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 20w51a.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
import mcpython.common.factory.BlockFactory
from mcpython import shared as G
from mcpython.util.enums import ToolType
import mcpython.common.mod.ModMcpython
from mcpython.common.factory import CombinedBlockFactory
from mcpython.common.data.gen.DataGeneratorManager import DataGeneratorInstance
from mcpython.common.config import ENABLED_EXTRA_BLOCKS as BLOCKS


def remove_if_downer_block_not_solid(instance):
    """
    Helper function for downer implementation.
    Will remove THIS block when the block below is air or an not-generated block
    :param instance: the block-instance to check
    """
    x, y, z = instance.position
    other = G.world.get_active_dimension_by_name(instance.dimension).get_block(
        (x, y - 1, z)
    )
    if other is None or type(other) == str:
        G.world.get_active_dimension_by_name(instance.dimension).remove_block(
            instance.position
        )


# todo: let this generate from java source
def load_blocks():
    full_template = (
        mcpython.common.factory.BlockFactory.BlockFactory()
        .set_global_mod_name("minecraft")
        .set_template()
    )
    log_template = full_template.copy().reset_template().set_log().set_template()
    falling_template = (
        full_template.copy().reset_template().set_fall_able().set_template()
    )
    slab_template = full_template.copy().reset_template().set_slab().set_template()

    full_template.set_name("ancient_debris").finish()
    full_template.set_name("barrier").set_break_able_flag(False).set_all_side_solid(
        False
    ).finish()
    full_template.set_name("chiseled_quartz_block").set_strength(
        0.8
    ).set_assigned_tools(ToolType.PICKAXE).set_minimum_tool_level(1).finish()
    full_template.set_name("quartz_block").set_strength(0.8).set_assigned_tools(
        ToolType.PICKAXE
    ).set_minimum_tool_level(1).finish()
    slab_template.set_name("quartz_slab").set_strength(0.8).set_assigned_tools(
        ToolType.PICKAXE
    ).set_minimum_tool_level(1).finish()
    full_template.set_name("smooth_stone").set_strength(1.5, 6).set_assigned_tools(
        ToolType.PICKAXE
    ).set_minimum_tool_level(1).finish()
    slab_template.set_name("smooth_stone_slab").set_strength(1.5, 6).set_assigned_tools(
        ToolType.PICKAXE
    ).set_minimum_tool_level(1).finish()

    full_template.set_name("cut_red_sandstone").finish()
    slab_template.set_name("cut_red_sandstone_slab").finish()
    full_template.set_name("cut_sandstone").finish()
    slab_template.set_name("cut_sandstone_slab").finish()

    full_template.set_name("red_sandstone").finish()
    slab_template.set_name("red_sandstone_slab").finish()

    full_template.set_name("sandstone").finish()
    slab_template.set_name("sandstone_slab").finish()

    full_template.set_name("dried_kelp_block").finish()

    log_template.set_name("minecraft:hay_block").finish()

    full_template.set_name("pumpkin").finish()
    full_template.set_name("jack_o_lantern").set_horizontal_orientable().finish()
    full_template.set_name("melon").finish()

    full_template.set_name("mycelium").set_default_model_state(
        {"snowy": "false"}
    ).finish()
    full_template.set_name("podzol").set_default_model_state(
        {"snowy": "false"}
    ).finish()

    full_template.set_name("netherrack").finish()

    full_template.set_name("quartz_block").finish()
    slab_template.set_name("quartz_slab").finish()


mcpython.common.mod.ModMcpython.mcpython.eventbus.subscribe(
    "stage:block:factory_usage", load_blocks, info="loading block definitions"
)


@G.mod_loader("minecraft", "stage:combined_factory:blocks")
def combined_load():
    GENERATOR = DataGeneratorInstance("{local}/resources/generated")
    GENERATOR.default_namespace = "minecraft"
    load_misc(GENERATOR)
    load_wood(GENERATOR)
    load_value_ables(GENERATOR)
    load_stones(GENERATOR)
    load_colored(GENERATOR)


def load_misc(generator: DataGeneratorInstance):
    CombinedBlockFactory.generate_log_block(
        generator,
        "minecraft:bone_block",
        front_texture="minecraft:block/bone_block_top",
        side_texture="minecraft:block/bone_block_side",
        callback=lambda _, factory: factory.set_strength(2)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1),
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:clay",
        callback=lambda _, factory: factory.set_strength(0.6).set_assigned_tools(
            ToolType.SHOVEL
        ),
        enable=BLOCKS,
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:honeycomb_block",
        callback=lambda _, factory: factory.set_strength(0.6),
        enable=BLOCKS,
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:magma_block",
        texture="minecraft:block/magma",
        enable=BLOCKS,
        callback=lambda _, factory: factory.set_strength(0.5)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:nether_wart_block",
        enable=BLOCKS,
        callback=lambda _, factory: factory.set_strength(1).set_assigned_tools(
            ToolType.HOE
        ),
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:warped_wart_block",
        enable=BLOCKS,
        callback=lambda _, factory: factory.set_strength(1).set_assigned_tools(
            ToolType.HOE
        ),
    )

    def set_purpur_block(_, factory):
        factory.set_strength(6, 1.5).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:purpur_block", callback=set_purpur_block, enable=BLOCKS
    )
    CombinedBlockFactory.generate_log_block(
        generator, "minecraft:purpur_pillar", callback=set_purpur_block
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:shroomlight",
        callback=lambda _, factory: factory.set_strength(1).set_assigned_tools(
            ToolType.HOE
        ),
        enable=BLOCKS,
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:snow_block",
        texture="minecraft:block/snow",
        enable=(True, False, BLOCKS),
        callback=lambda _, factory: factory.set_strength(0.2)
        .set_assigned_tools(ToolType.SHOVEL)
        .set_minimum_tool_level(1),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:soul_sand",
        enable=BLOCKS,
        callback=lambda _, factory: factory.set_strength(0.5).set_assigned_tools(
            ToolType.SHOVEL
        ),
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:soul_soil",
        enable=BLOCKS,
        callback=lambda _, factory: factory.set_strength(0.5).set_assigned_tools(
            ToolType.SHOVEL
        ),
    )

    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:sponge",
        callback=lambda _, factory: factory.set_strength(0.6).set_assigned_tools(
            ToolType.HOE
        ),
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:wet_sponge",
        callback=lambda _, factory: factory.set_strength(0.6).set_assigned_tools(
            ToolType.HOE
        ),
    )


def load_wood(generator: DataGeneratorInstance):
    def set_wood(_, factory):
        factory.set_strength(2).set_assigned_tools(ToolType.AXE)

    def set_stem(_, factory):
        factory.set_strength(1, 2).set_assigned_tools(ToolType.AXE)

    def set_leaves(_, factory):
        factory.set_strength(0.2).set_assigned_tools(ToolType.SHEAR).set_all_side_solid(
            False
        )

    for wood_type in ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]:
        CombinedBlockFactory.generate_log_block(
            generator, "minecraft:{}_log".format(wood_type), callback=set_wood
        )
        CombinedBlockFactory.generate_log_block(
            generator, "minecraft:stripped_{}_log".format(wood_type), callback=set_wood
        )
        CombinedBlockFactory.generate_log_block(
            generator,
            "minecraft:{}_wood".format(wood_type),
            front_texture="minecraft:block/{}_log".format(wood_type),
            side_texture="minecraft:block/{}_log".format(wood_type),
            callback=set_wood,
        )
        CombinedBlockFactory.generate_log_block(
            generator,
            "minecraft:stripped_{}_wood".format(wood_type),
            front_texture="minecraft:block/stripped_{}_log".format(wood_type),
            side_texture="minecraft:block/stripped_{}_log".format(wood_type),
            callback=set_wood,
        )

        CombinedBlockFactory.generate_full_block(
            generator, "minecraft:{}_leaves".format(wood_type), callback=set_leaves
        )

    for wood_type in ["crimson", "warped"]:
        CombinedBlockFactory.generate_log_block(
            generator, "minecraft:{}_stem".format(wood_type), callback=set_stem
        )
        CombinedBlockFactory.generate_log_block(
            generator, "minecraft:stripped_{}_stem".format(wood_type), callback=set_stem
        )
        CombinedBlockFactory.generate_log_block(
            generator,
            "minecraft:{}_hyphae".format(wood_type),
            front_texture="minecraft:block/{}_stem".format(wood_type),
            side_texture="minecraft:block/{}_stem".format(wood_type),
            callback=set_stem,
        )
        CombinedBlockFactory.generate_log_block(
            generator,
            "minecraft:stripped_{}_hyphae".format(wood_type),
            front_texture="minecraft:block/stripped_{}_stem".format(wood_type),
            side_texture="minecraft:block/stripped_{}_stem".format(wood_type),
            callback=set_stem,
        )

    for wood_type in [
        "oak",
        "spruce",
        "birch",
        "jungle",
        "acacia",
        "dark_oak",
        "crimson",
        "warped",
    ]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            generator,
            "minecraft:{}_planks".format(wood_type),
            enable=BLOCKS,
            slab_name="minecraft:{}_slab".format(wood_type),
            wall_name="minecraft:{}_wall".format(wood_type),
            callback=set_wood,
        )


def load_value_ables(generator: DataGeneratorInstance):
    def set_quartz(_, factory):
        factory.set_strength(0.8).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    def set_material_block(_, factory):
        factory.set_strength(5, 6).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(3)

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:netherite_block",
        callback=lambda _, factory: factory.set_strength(50, 1200)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(5),
        enable=BLOCKS,
    )

    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:nether_quartz_ore",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:quartz_bricks",
        callback=set_quartz,
        enable=BLOCKS,
        slab_name="minecraft:quartz_brick_slab",
        wall_name="minecraft:quartz_brick_wall",
    )
    CombinedBlockFactory.generate_log_block(
        generator, "minecraft:quartz_pillar", callback=set_quartz
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:smooth_quartz",
        callback=set_quartz,
        texture="minecraft:block/quartz_block_bottom",
        enable=BLOCKS,
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:coal_block",
        callback=lambda _, factory: factory.set_strength(5, 6)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1),
        enable=BLOCKS,
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:coal_ore",
        callback=lambda _, factory: factory.set_strength(3, 3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:diamond_block", callback=set_material_block, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:diamond_ore",
        callback=lambda _, factory: factory.set_strength(3, 3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(3),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:emerald_block", callback=set_material_block, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:emerald_ore",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(3),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:glowstone",
        callback=lambda _, factory: factory.set_strength(0.3),
        enable=BLOCKS,
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:gold_block", callback=set_material_block, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:gold_ore",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(3),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:iron_block", callback=set_material_block, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:iron_ore",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(2),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:lapis_block",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(2),
        enable=BLOCKS,
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:lapis_ore",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(2),
    )

    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:nether_gold_ore",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(1),
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:redstone_block",
        callback=lambda _, factory: factory.set_strength(5, 6).set_assigned_tools(
            ToolType.PICKAXE
        ),
        enable=BLOCKS,
    )
    CombinedBlockFactory.generate_full_block(
        generator,
        "minecraft:redstone_ore",
        callback=lambda _, factory: factory.set_strength(3)
        .set_assigned_tools(ToolType.PICKAXE)
        .set_minimum_tool_level(3),
    )


def load_stones(generator: DataGeneratorInstance):
    def set_stone(_, factory):
        factory.set_strength(1.5, 6).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    def set_basalt(_, factory):
        factory.set_strength(1.25, 4.2).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    def set_bedrock(_, factory):
        factory.set_strength(-1, 3600000).set_break_able_flag(False)

    def set_end_stone(_, factory):
        factory.set_strength(3, 9).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    for name in ["andesite", "granite", "diorite"]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            generator, "minecraft:{}".format(name), callback=set_stone
        )
        CombinedBlockFactory.generate_full_block_slab_wall(
            generator,
            "minecraft:polished_{}".format(name),
            callback=set_stone,
            enable=BLOCKS,
        )

    CombinedBlockFactory.generate_log_block(
        generator,
        "minecraft:basalt",
        callback=set_basalt,
        front_texture="minecraft:block/basalt_top",
        side_texture="minecraft:block/basalt_side",
    )
    CombinedBlockFactory.generate_log_block(
        generator,
        "minecraft:polished_basalt",
        callback=set_basalt,
        front_texture="minecraft:block/polished_basalt_top",
        side_texture="minecraft:block/polished_basalt_side",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:blackstone", callback=set_stone
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:chiseled_polished_blackstone",
        callback=set_stone,
        enable=BLOCKS,
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:cracked_polished_blackstone_bricks",
        callback=set_stone,
        enable=BLOCKS,
        slab_name="minecraft:cracked_polished_blackstone_brick_slab",
        wall_name="minecraft:cracked_polished_blackstone_brick_wall",
    )
    CombinedBlockFactory.generate_full_block(
        generator, "minecraft:gilded_blackstone", callback=set_stone
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:polished_blackstone", callback=set_stone
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:polished_blackstone_bricks",
        callback=set_stone,
        slab_name="minecraft:polished_blackstone_brick_slab",
        wall_name="minecraft:polished_blackstone_brick_wall",
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:bedrock", callback=set_bedrock, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:chiseled_stone_bricks",
        callback=set_stone,
        enable=BLOCKS,
        slab_name="minecraft:chiseled_stone_brick_slab",
        wall_name="minecraft:chiseled_stone_brick_wall",
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:cobblestone", callback=set_stone
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:stone", enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:stone_bricks",
        slab_name="minecraft:stone_brick_slab",
        wall_name="minecraft:stone_brick_wall",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:mossy_stone_bricks",
        slab_name="minecraft:mossy_stone_brick_slab",
        wall_name="minecraft:mossy_stone_brick_wall",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:cracked_stone_bricks",
        callback=set_stone,
        enable=BLOCKS,
        slab_name="minecraft:cracked_stone_brick_slab",
        wall_name="minecraft:cracked_stone_brick_wall",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:mossy_cobblestone", callback=set_stone
    )

    def set_dirt(_, factory):
        factory.set_strength(0.5).set_assigned_tools(ToolType.SHOVEL)

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:coarse_dirt", callback=set_dirt, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:dirt", callback=set_dirt, enable=BLOCKS
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:end_stone", callback=set_end_stone, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:end_stone_bricks",
        callback=set_end_stone,
        slab_name="minecraft:end_stone_brick_slab",
        wall_name="minecraft:end_stone_brick_wall",
    )

    def set_obsidian(_, factory):
        factory.set_strength(50, 1200).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(5)

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:obsidian", callback=set_obsidian, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:crying_obsidian", callback=set_obsidian, enable=BLOCKS
    )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:dark_prismarine", callback=set_stone, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:prismarine", callback=set_stone
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:prismarine_bricks",
        slab_name="minecraft:prismarine_brick_slab",
        wall_name="minecraft:prismarine_brick_wall",
        callback=set_stone,
        enable=BLOCKS,
    )

    def set_fall_able(_, factory):
        factory.set_strength(0.6).set_assigned_tools(ToolType.SHOVEL).set_fall_able()

    CombinedBlockFactory.generate_full_block(
        generator, "minecraft:gravel", callback=set_fall_able
    )
    CombinedBlockFactory.generate_full_block(
        generator, "minecraft:sand", callback=set_fall_able
    )
    CombinedBlockFactory.generate_full_block(
        generator, "minecraft:red_sand", callback=set_fall_able
    )


def load_colored(generator: DataGeneratorInstance):
    def set_concrete(_, factory):
        factory.set_strength(1.8).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    def set_concrete_powder(_, factory):
        factory.set_strength(0.5).set_assigned_tools(ToolType.SHOVEL).set_fall_able()

    def set_terracotta(_, factory):
        factory.set_strength(1.25, 4.2).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    def set_wool(_, factory):
        factory.set_strength(0.8).set_assigned_tools(ToolType.SHEAR)

    def set_stained_glass(_, factory):
        factory.set_strength(0.3).set_all_side_solid(False)

    def set_brick(_, factory):
        factory.set_strength(2, 6).set_assigned_tools(
            ToolType.PICKAXE
        ).set_minimum_tool_level(1)

    for color in [
        "white",
        "orange",
        "magenta",
        "light_blue",
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
    ]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            generator,
            "minecraft:{}_concrete".format(color),
            callback=set_concrete,
            enable=BLOCKS,
        )
        CombinedBlockFactory.generate_full_block(
            generator,
            "minecraft:{}_concrete_powder".format(color),
            callback=set_concrete_powder,
        )
        CombinedBlockFactory.generate_full_block_slab_wall(
            generator,
            "minecraft:{}_terracotta".format(color),
            callback=set_terracotta,
            enable=BLOCKS,
        )
        CombinedBlockFactory.generate_full_block_slab_wall(
            generator,
            "minecraft:{}_wool".format(color),
            callback=set_wool,
            enable=BLOCKS,
        )
        CombinedBlockFactory.generate_full_block_slab_wall(
            generator,
            "minecraft:{}_stained_glass".format(color),
            callback=set_stained_glass,
            enable=BLOCKS,
        )

    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:terracotta", callback=set_terracotta, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator, "minecraft:glass", callback=set_stained_glass, enable=BLOCKS
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:bricks",
        callback=set_brick,
        slab_name="minecraft:brick_slab",
        wall_name="minecraft:brick_wall",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:chiseled_nether_bricks",
        callback=set_brick,
        enable=BLOCKS,
        slab_name="minecraft:chiseled_nether_brick_slab",
        wall_name="minecraft:chiseled_nether_brick_wall",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:cracked_nether_bricks",
        callback=set_brick,
        enable=BLOCKS,
        slab_name="minecraft:cracked_nether_brick_slab",
        wall_name="minecraft:cracked_nether_brick_wall",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:red_nether_bricks",
        callback=set_brick,
        slab_name="minecraft:red_nether_brick_slab",
        wall_name="minecraft:red_nether_brick_wall",
    )
    CombinedBlockFactory.generate_full_block_slab_wall(
        generator,
        "minecraft:nether_bricks",
        callback=set_brick,
        slab_name="minecraft:nether_brick_slab",
        wall_name="minecraft:nether_brick_wall",
    )
