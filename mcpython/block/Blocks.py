"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.factory.BlockFactory
import globals as G
from mcpython.util.enums import ToolType
import mcpython.mod.ModMcpython
from mcpython.factory import CombinedBlockFactory
import mcpython.datagen.Configuration
from mcpython.factory.BlockFactory import BlockFactory
from mcpython.datagen.Configuration import DataGeneratorConfig
from mcpython.config import ENABLED_EXTRA_BLOCKS as BLOCKS


def remove_if_downer_block_not_solid(blockinstance):
    """
    Helper function for donwer implementation.
    Will remove THIS block when the block below is air or an not-generated block
    :param blockinstance: the block-instance to check
    """
    x, y, z = blockinstance.position
    other = G.world.get_active_dimension().get_block((x, y - 1, z))
    if other is None or type(other) == str:
        G.world.get_active_dimension().remove_block(blockinstance.position)


# todo: let this generate from java source
def load_blocks():
    full_template = mcpython.factory.BlockFactory.BlockFactory().setGlobalModName("minecraft").setTemplate()
    log_template = full_template.copy().resetTemplate().setLog().setTemplate()
    falling_template = full_template.copy().resetTemplate().setFallable().setTemplate()
    slab_template = full_template.copy().resetTemplate().setSlab().setTemplate()

    full_template.setName("ancient_debris").finish()
    full_template.setName("barrier").setBreakAbleFlag(False).setAllSideSolid(False).finish()
    full_template.setName("chiseled_quartz_block").setStrenght(.8).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    full_template.setName("quartz_block").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("quartz_slab").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("smooth_stone").setStrenght(1.5, 6).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("smooth_stone_slab").setStrenght(1.5, 6).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    full_template.setName("cut_red_sandstone").finish()
    slab_template.setName("cut_red_sandstone_slab").finish()
    full_template.setName("cut_sandstone").finish()
    slab_template.setName("cut_sandstone_slab").finish()

    full_template.setName("red_sandstone").finish()
    slab_template.setName("red_sandstone_slab").finish()

    full_template.setName("sandstone").finish()
    slab_template.setName("sandstone_slab").finish()

    full_template.setName("dried_kelp_block").finish()

    log_template.setName("minecraft:hay_block").finish()

    full_template.setName("pumpkin").finish()
    full_template.setName("jack_o_lantern").setHorizontalOrientable().finish()
    full_template.setName("melon").finish()

    full_template.setName("mycelium").setDefaultModelState({"snowy": "false"}).finish()
    full_template.setName("podzol").setDefaultModelState({"snowy": "false"}).finish()

    full_template.setName("netherrack").finish()

    full_template.setName("quartz_block").finish()
    slab_template.setName("quartz_slab").finish()


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:factory_usage", load_blocks,
                                                     info="loading block definitions")


@G.modloader("minecraft", "stage:combined_factory:blocks")
def combined_load():
    config = DataGeneratorConfig("minecraft", G.local + "/resources/generated")
    config.setDefaultNamespace("minecraft")

    load_misc(config)
    load_wood(config)
    load_value_ables(config)
    load_stones(config)
    load_colored(config)


def load_misc(config: DataGeneratorConfig):
    CombinedBlockFactory.generate_log_block(
        config, "minecraft:bone_block", front_texture="minecraft:block/bone_block_top",
        side_texture="minecraft:block/bone_block_side",
        callback=lambda _, factory: factory.setStrenght(2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1))
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:clay", callback=lambda _, factory: factory.setStrenght(.6).setBestTools(ToolType.SHOVEL),
        enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:honeycomb_block", callback=lambda _, factory: factory.setStrenght(.6), enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:magma_block", texture="minecraft:block/magma", enable=BLOCKS,
        callback=lambda _, factory: factory.setStrenght(.5).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:nether_wart_block", enable=BLOCKS,
        callback=lambda _, factory: factory.setStrenght(1).setBestTools(ToolType.HOE))
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:warped_wart_block", enable=BLOCKS,
        callback=lambda _, factory: factory.setStrenght(1).setBestTools(ToolType.HOE))

    def set_purpur_block(_, factory): factory.setStrenght(6, 1.5).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:purpur_block", callback=set_purpur_block, enable=BLOCKS)
    CombinedBlockFactory.generate_log_block(config, "minecraft:purpur_pillar", callback=set_purpur_block)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:shroomlight", callback=lambda _, factory: factory.setStrenght(1).setBestTools(ToolType.HOE),
        enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:snow_block", texture="minecraft:block/snow", enable=(True, False, BLOCKS),
        callback=lambda _, factory: factory.setStrenght(.2).setBestTools(ToolType.SHOVEL).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:soul_sand", enable=BLOCKS,
        callback=lambda _, factory: factory.setStrenght(.5).setBestTools(ToolType.SHOVEL))
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:soul_soil", enable=BLOCKS,
        callback=lambda _, factory: factory.setStrenght(.5).setBestTools(ToolType.SHOVEL))

    CombinedBlockFactory.generate_full_block(
        config, "minecraft:sponge", callback=lambda _, factory: factory.setStrenght(.6).setBestTools(ToolType.HOE))
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:wet_sponge", callback=lambda _, factory: factory.setStrenght(.6).setBestTools(ToolType.HOE))


def load_wood(config: DataGeneratorConfig):

    def set_wood(_, factory): factory.setStrenght(2).setBestTools(ToolType.AXE)
    def set_stem(_, factory): factory.setStrenght(1, 2).setBestTools(ToolType.AXE)
    def set_leaves(_, factory): factory.setStrenght(.2).setBestTools(ToolType.SHEAR).setAllSideSolid(False)

    for wood_type in ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]:
        CombinedBlockFactory.generate_log_block(config, "minecraft:{}_log".format(wood_type), callback=set_wood)
        CombinedBlockFactory.generate_log_block(config, "minecraft:stripped_{}_log".format(wood_type),
                                                callback=set_wood)
        CombinedBlockFactory.generate_log_block(
            config, "minecraft:{}_wood".format(wood_type), front_texture="minecraft:block/{}_log".format(wood_type),
            side_texture="minecraft:block/{}_log".format(wood_type), callback=set_wood)
        CombinedBlockFactory.generate_log_block(
            config, "minecraft:stripped_{}_wood".format(wood_type),
            front_texture="minecraft:block/stripped_{}_log".format(wood_type),
            side_texture="minecraft:block/stripped_{}_log".format(wood_type), callback=set_wood)

        CombinedBlockFactory.generate_full_block(
            config, "minecraft:{}_leaves".format(wood_type), callback=set_leaves,
            texture="build/texture/blocks/{}_leaves.png".format(wood_type))

    for wood_type in ["crimson", "warped"]:
        CombinedBlockFactory.generate_log_block(config, "minecraft:{}_stem".format(wood_type), callback=set_stem)
        CombinedBlockFactory.generate_log_block(config, "minecraft:stripped_{}_stem".format(wood_type),
                                                callback=set_stem)
        CombinedBlockFactory.generate_log_block(
            config, "minecraft:{}_hyphae".format(wood_type), front_texture="minecraft:block/{}_stem".format(wood_type),
            side_texture="minecraft:block/{}_stem".format(wood_type), callback=set_stem)
        CombinedBlockFactory.generate_log_block(
            config, "minecraft:stripped_{}_hyphae".format(wood_type),
            front_texture="minecraft:block/stripped_{}_stem".format(wood_type),
            side_texture="minecraft:block/stripped_{}_stem".format(wood_type), callback=set_stem)

    for wood_type in ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "crimson", "warped"]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_planks".format(wood_type), enable=BLOCKS,
            slab_name="minecraft:{}_slab".format(wood_type), wall_name="minecraft:{}_wall".format(wood_type),
            callback=set_wood)


def load_value_ables(config: DataGeneratorConfig):
    def set_quartz(_, factory): factory.setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)
    def set_material_block(_, factory): factory.setStrenght(5, 6).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:netherite_block", callback=lambda _, factory: factory.setStrenght(50, 1200).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(5), enable=BLOCKS)

    CombinedBlockFactory.generate_full_block(
        config, "minecraft:nether_quartz_ore", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:quartz_bricks", callback=set_quartz, enable=BLOCKS, slab_name="minecraft:quartz_brick_slab",
        wall_name="minecraft:quartz_brick_wall")
    CombinedBlockFactory.generate_log_block(config, "minecraft:quartz_pillar", callback=set_quartz)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:smooth_quartz", callback=set_quartz, texture="minecraft:block/quartz_block_bottom",
        enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:coal_block", callback=lambda _, factory: factory.setStrenght(5, 6).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1), enable=BLOCKS)
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:coal_ore", callback=lambda _, factory: factory.setStrenght(3, 3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:diamond_block", callback=set_material_block, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:diamond_ore", callback=lambda _, factory: factory.setStrenght(3, 3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(3))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:emerald_block", callback=set_material_block, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:emerald_ore", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(3))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:glowstone", callback=lambda _, factory: factory.setStrenght(.3), enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:gold_block", callback=set_material_block, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:gold_ore", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(3))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:iron_block", callback=set_material_block, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:iron_ore", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(2))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:lapis_block", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(2), enable=BLOCKS)
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:lapis_ore", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(2))

    CombinedBlockFactory.generate_full_block(
        config, "minecraft:nether_gold_ore", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1))

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:redstone_block", callback=lambda _, factory: factory.setStrenght(5, 6).setBestTools(
            ToolType.PICKAXE), enable=BLOCKS)
    CombinedBlockFactory.generate_full_block(
        config, "minecraft:redstone_ore", callback=lambda _, factory: factory.setStrenght(3).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(3))


def load_stones(config: DataGeneratorConfig):
    def set_stone(_, factory): factory.setStrenght(1.5, 6).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)
    def set_basalt(_, factory): factory.setStrenght(1.25, 4.2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)
    def set_bedrock(_, factory): factory.setStrenght(-1, 3600000).setBreakAbleFlag(False)
    def set_end_stone(_, factory): factory.setStrenght(3, 9).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)

    for name in ["andesite", "granite", "diorite"]:
        CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:{}".format(name), callback=set_stone)
        CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:polished_{}".format(name),
                                                           callback=set_stone, enable=BLOCKS)

    CombinedBlockFactory.generate_log_block(
        config, "minecraft:basalt", callback=set_basalt, front_texture="minecraft:block/basalt_top",
        side_texture="minecraft:block/basalt_side")
    CombinedBlockFactory.generate_log_block(
        config, "minecraft:polished_basalt", callback=set_basalt, front_texture="minecraft:block/polished_basalt_top",
        side_texture="minecraft:block/polished_basalt_side")
    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:blackstone", callback=set_stone)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:chiseled_polished_blackstone", callback=set_stone, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:cracked_polished_blackstone_bricks", callback=set_stone, enable=BLOCKS,
        slab_name="minecraft:cracked_polished_blackstone_brick_slab",
        wall_name="minecraft:cracked_polished_blackstone_brick_wall")
    CombinedBlockFactory.generate_full_block(config, "minecraft:gilded_blackstone", callback=set_stone)
    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:polished_blackstone", callback=set_stone)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:polished_blackstone_bricks", callback=set_stone,
        slab_name="minecraft:polished_blackstone_brick_slab", wall_name="minecraft:polished_blackstone_brick_wall")

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:bedrock", callback=set_bedrock, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:chiseled_stone_bricks", callback=set_stone, enable=BLOCKS,
        slab_name="minecraft:chiseled_stone_brick_slab", wall_name="minecraft:chiseled_stone_brick_wall")

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:cobblestone", callback=set_stone)

    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:stone", enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:stone_bricks", slab_name="minecraft:stone_brick_slab",
        wall_name="minecraft:stone_brick_wall")
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:mossy_stone_bricks", slab_name="minecraft:mossy_stone_brick_slab",
        wall_name="minecraft:mossy_stone_brick_wall")
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:cracked_stone_bricks", callback=set_stone, enable=BLOCKS,
        slab_name="minecraft:cracked_stone_brick_slab", wall_name="minecraft:cracked_stone_brick_wall")
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:mossy_cobblestone", callback=set_stone)

    def set_dirt(_, factory): factory.setStrenght(.5).setBestTools(ToolType.SHOVEL)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:coarse_dirt", callback=set_dirt, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:dirt", callback=set_dirt, enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:end_stone", callback=set_end_stone, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:end_stone_bricks", callback=set_end_stone, slab_name="minecraft:end_stone_brick_slab",
        wall_name="minecraft:end_stone_brick_wall")

    def set_obsidian(_, factory): factory.setStrenght(50, 1200).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(5)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:obsidian", callback=set_obsidian, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:crying_obsidian", callback=set_obsidian, enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:dark_prismarine", callback=set_stone, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:prismarine", callback=set_stone)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:prismarine_bricks", slab_name="minecraft:prismarine_brick_slab",
        wall_name="minecraft:prismarine_brick_wall", callback=set_stone, enable=BLOCKS)

    def set_fall_able(_, factory): factory.setStrenght(.6).setBestTools(ToolType.SHOVEL).setFallable()

    CombinedBlockFactory.generate_full_block(config, "minecraft:gravel", callback=set_fall_able)
    CombinedBlockFactory.generate_full_block(config, "minecraft:sand", callback=set_fall_able)
    CombinedBlockFactory.generate_full_block(config, "minecraft:red_sand", callback=set_fall_able)


def load_colored(config: DataGeneratorConfig):
    def set_concrete(_, factory): factory.setStrenght(1.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)
    def set_concrete_powder(_, factory): factory.setStrenght(.5).setBestTools(ToolType.SHOVEL).setFallable()
    def set_terracotta(_, factory): factory.setStrenght(1.25, 4.2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)
    def set_wool(_, factory): factory.setStrenght(.8).setBestTools(ToolType.SHEAR)
    def set_stained_glass(_, factory): factory.setStrenght(.3).setAllSideSolid(False)
    def set_brick(_, factory): factory.setStrenght(2, 6).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1)

    for color in ["white", "orange", "magenta", "light_blue", "lime", "pink", "gray", "light_gray", "cyan",
                  "purple", "blue", "brown", "green", "red", "black"]:
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_concrete".format(color), callback=set_concrete, enable=BLOCKS)
        CombinedBlockFactory.generate_full_block(
            config, "minecraft:{}_concrete_powder".format(color), callback=set_concrete_powder)
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_terracotta".format(color), callback=set_terracotta, enable=BLOCKS)
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_wool".format(color), callback=set_wool, enable=BLOCKS)
        CombinedBlockFactory.generate_full_block_slab_wall(
            config, "minecraft:{}_stained_glass".format(color), callback=set_stained_glass, enable=BLOCKS)

    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:terracotta", callback=set_terracotta, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:glass", callback=set_stained_glass, enable=BLOCKS)
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:bricks", callback=set_brick, slab_name="minecraft:brick_slab",
        wall_name="minecraft:brick_wall")
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:chiseled_nether_bricks", callback=set_brick, enable=BLOCKS,
        slab_name="minecraft:chiseled_nether_brick_slab", wall_name="minecraft:chiseled_nether_brick_wall")
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:cracked_nether_bricks", callback=set_brick, enable=BLOCKS,
        slab_name="minecraft:cracked_nether_brick_slab", wall_name="minecraft:cracked_nether_brick_wall")
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:red_nether_bricks", callback=set_brick,
        slab_name="minecraft:red_nether_brick_slab", wall_name="minecraft:red_nether_brick_wall")
    CombinedBlockFactory.generate_full_block_slab_wall(
        config, "minecraft:nether_bricks", callback=set_brick,
        slab_name="minecraft:nether_brick_slab", wall_name="minecraft:nether_brick_wall")

