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

    colors = mcpython.util.enums.COLORS

    # missing: air

    # full_template.setName("stone").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    full_template.setName("granite").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    full_template.setName("polished_granite").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("diorite").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    full_template.setName("polished_diorite").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("andesite").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("polished_andesite").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("dirt").setStrenght(.5).setBestTools(ToolType.SHOVEL).finish()
    full_template.setName("coarse_dirt").setStrenght(.5).setBestTools(ToolType.SHOVEL).finish()
    full_template.setName("podzol").setDefaultModelState({"snowy": "false"}).setStrenght(.5).setBestTools(
        ToolType.SHOVEL).finish()
    full_template.setName("cobblestone").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    full_template.setName("oak_planks").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    full_template.setName("spruce_planks").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    full_template.setName("birch_planks").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    full_template.setName("jungle_planks").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    full_template.setName("acacia_planks").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    full_template.setName("dark_oak_planks").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()

    # missing: oak, spruce, birch, jungle, acacia and dark oak saplings

    full_template.setName("bedrock").setStrenght(-1, 3600000).finish()

    # missing: water and lava

    falling_template.setName("sand").setStrenght(.5).setBestTools(ToolType.SHOVEL).finish()
    falling_template.setName("red_sand").setStrenght(.5).setBestTools(ToolType.SHOVEL).finish()
    falling_template.setName("gravel").setStrenght(.6).setBestTools(ToolType.SHOVEL).finish()

    full_template.setName("gold_ore").setStrenght(3., 3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()
    full_template.setName("iron_ore").setStrenght(3., 3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(2).finish()
    full_template.setName("coal_ore").setStrenght(3., 3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    log_template.setName("oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("spruce_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("birch_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("jungle_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("acacia_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("dark_oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    log_template.setName("stripped_oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_spruce_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_birch_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_jungle_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_acacia_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_dark_oak_log").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    log_template.setName("oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("spruce_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("birch_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("jungle_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("acacia_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("dark_oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    log_template.setName("stripped_oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_spruce_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_birch_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_jungle_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_acacia_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()
    log_template.setName("stripped_dark_oak_wood").setStrenght(2.).setBestTools(ToolType.AXE).finish()

    full_template.setName("oak_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("spruce_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("birch_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("jungle_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("acacia_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()
    full_template.setName("dark_oak_leaves").setAllSideSolid(False).setStrenght(.2).enableRandomTicks().setBestTools(
        ToolType.SHEAR).finish()

    full_template.setName("sponge").setStrenght(.6).finish()
    full_template.setName("wet_sponge").setStrenght(.6).finish()

    full_template.setName("glass").setAllSideSolid(False).setStrenght(.3).setBestTools(ToolType.PICKAXE).finish()

    full_template.setName("lapis_ore").setStrenght(3).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(2).finish()
    full_template.setName("lapis_block").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(2).finish()

    # missing: dispenser

    full_template.setName("sandstone").setBestTools(ToolType.PICKAXE).setStrenght(.8).setMinimumToolLevel(1).finish()
    full_template.setName("cut_sandstone").setBestTools(ToolType.PICKAXE).setStrenght(.8).setMinimumToolLevel(
        1).finish()

    # missing: note block; white, orange, magenta, light blue, yellow, lime, pink, gray, light gray, cyan, purple, blue,
    # brown, green, red and black bed; powered and detector rail, sticky piston, cobweb, grass, fern, dead bush,
    # seagrass, tall seagrass, piston

    full_template.setName("white_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("orange_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("magenta_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("light_blue_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("yellow_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("lime_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("pink_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("gray_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("light_gray_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("cyan_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("purple_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("blue_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("brown_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("green_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("red_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()
    full_template.setName("black_wool").setStrenght(.6).setBestTools(ToolType.SHEAR).finish()

    # missing: dandelion, poppy, blue orchid, allium, azure bluet, red tulip, orange tulip, white tulip, pink tulip,
    # oxeye daisy, cornflower, wither rose, lily of the valley, brown mushroom

    full_template.setName("gold_block").setStrenght(3., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()
    full_template.setName("iron_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        2).finish()

    full_template.setName("bricks").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing: tnt

    full_template.setName("bookshelf").setStrenght(1.5).setBestTools(ToolType.AXE).finish()

    full_template.setName("mossy_cobblestone").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("obsidian").setStrenght(50., 1200.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: torch, fire, spawner, oak, spruce, birch, jungle, acacia and dark oak stairs, redstone wire

    full_template.setName("diamond_ore").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()
    full_template.setName("diamond_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: wheat, farmland; oak, spruce, birch, jungle, acacia and dark oak signs & doors & pressure plates, ladder,
    # rail, lever, stone pressure plate

    full_template.setName("redstone_ore").setStrenght(3.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(3).finish()  # setDefaultModelState({"lit": "false"}).

    # missing: redstone torch, stone button, snow

    full_template.setName("ice").setSpeedMultiplier(1.98).setStrenght(.5).setAllSideSolid(False).setBestTools(
        ToolType.PICKAXE).finish()
    full_template.setName("snow_block").setStrenght(.2).setBestTools(ToolType.SHOVEL).finish()

    # missing: cactus

    full_template.setName("clay").setStrenght(.6).setBestTools(ToolType.SHOVEL).finish()

    # missing: sugar can, jukebox

    full_template.setName("pumpkin").setStrenght(1.).setBestTools(ToolType.AXE).finish()
    full_template.setName("netherrack").setStrenght(.4).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    full_template.setName("soul_sand").setStrenght(.5).setSpeedMultiplier(.4).setBestTools(ToolType.SHOVEL).finish()
    full_template.setName("glowstone").setStrenght(.3).setBestTools(ToolType.PICKAXE).finish()

    # missing: nether portal

    full_template.setName("carved_pumpkin").setHorizontalOrientable().setStrenght(1.).setBestTools(
        ToolType.AXE).finish()
    full_template.setName("jack_o_lantern").setHorizontalOrientable().setStrenght(1.).setBestTools(
        ToolType.AXE).setBlockItemGeneratorState({"facing": "east"}).finish()

    # missing: cake, repeater

    for color in colors:
        full_template.setName("{}_stained_glass".format(color)).setAllSideSolid(False).setStrenght(.3).setBestTools(
            ToolType.PICKAXE).finish()

    # missing: oak, spruce, birch, jungle, acacia and dark oak trapdoors

    full_template.setName("stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("mossy_stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("cracked_stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE). \
        setMinimumToolLevel(1).finish()
    full_template.setName("chiseled_stone_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE). \
        setMinimumToolLevel(1).finish()

    # missing: infested stone, cobblestone, stone bricks, mossy stone bricks, cracked stone bricks and chiseled stone
    # bricks; brown and red mushroom block, iron bars, glass pane

    full_template.setName("melon").setStrenght(1.).setBestTools(ToolType.AXE).finish()

    # missing: attached pumpkin and melon stem, vine; oak, spruce, birch, jungle, acacia and dark oak fence gates, brick
    # stairs, stone brick stairs

    full_template.setName("mycelium").setDefaultModelState({"snowy": "false"}).setStrenght(.6).setBestTools(
        ToolType.SHOVEL).finish()

    # missing: lily pad

    full_template.setName("nether_bricks").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: nether brick stairs, nether wart, enchanting table, brewing stand, cauldron, end portal, end portal
    # frame

    full_template.setName("end_stone").setStrenght(3., 9.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: draggon egg, redstone lamp, cocoa, sandstone stairs

    full_template.setName("emerald_ore").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()

    # missing: tripwire hook, tripwire

    full_template.setName("emerald_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: beacon, flower pot; potted oak, spruce, birch, jungle, acacia and dark oak sapling, fern, dandelion,
    # poppy, blue orchid, allium, azure bluet, red tulip, orange tulip, white tulip, pink tulip, oxeye daisy,
    # cornflower, lily of the valley, wither rose, red mushroom, dead bish, cactus; carrots, potatoes,
    # oak, spruce, birch, jungle, acacia and dark oak buttons, skeleton skull, wither skeleton skull,
    # zombie head, player head, creeper head, dragon head, anvil, chipped anvil, damaged anvil, trapped chest,
    # light & heavy weighted pressure plate, comparator, daylight detector

    full_template.setName("redstone_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()
    full_template.setName("nether_quartz_ore").setStrenght(3.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: hopper

    full_template.setName("quartz_block").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(3).finish()
    full_template.setName("chiseled_quartz_block").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        3).finish()

    # missing: quartz stairs, activator rail, dropper

    for color in colors:
        full_template.setName("{}_terracotta".format(color)).setStrenght(1.25, 4.2).setBestTools(
            ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing colored glass panes, slime block

    full_template.setName("barrier").setAllSideSolid(False).setConductsRedstonePowerFlag(False).setCanMobsSpawnOnFlag(
        False).setSolidFlag(False).setBreakAbleFlag(False).setStrenght(-1, 3600000).finish()

    # missing: iron trapdoor

    full_template.setName("prismarine").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("prismarine_bricks").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("dark_prismarine").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("prismarine_slab").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("prismarine_brick_slab").setStrenght(1.5, 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("dark_prismarine_slab").setStrenght(1.5, 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing: prismarine stairs, prismarine brick stairs, dark prismarine stairs

    full_template.setName("sea_lantern").setStrenght(.3).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    log_template.setName("hay_block").setStrenght(.5).finish()

    full_template.setName("terracotta").setStrenght(1.25, 4.2).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    full_template.setName("coal_block").setStrenght(5., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("packed_ice").setStrenght(.5).setSpeedMultiplier(1.98).setBestTools(ToolType.PICKAXE).finish()

    # missing: sunflower, lilac, rose bush, peony, tall grass, large fern, colored banners

    full_template.setName("red_sandstone").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("chiseled_red_sandstone").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("cut_red_sandstone").setStrenght(.8).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: red sandstone stairs

    slab_template.setName("oak_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("spruce_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("birch_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("jungle_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("acacia_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("dark_oak_slab").setStrenght(2., 3.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("stone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("smooth_stone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("sandstone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("cut_sandstone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("petrified_oak_slab").setStrenght(2., 6.).setBestTools(ToolType.AXE).finish()
    slab_template.setName("cobblestone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("brick_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("stone_brick_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("nether_brick_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("quartz_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("red_sandstone_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    slab_template.setName("cut_red_sandstone_slab").setStrenght(2., 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("purpur_slab").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    full_template.setName("smooth_stone").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("smooth_sandstone").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("smooth_quartz").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    full_template.setName("smooth_red_sandstone").setStrenght(2., 6.).setBestTools(
        ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing: wooden doors, end rod, chorus plant, chorus flower

    full_template.setName("purpur_block").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()
    log_template.setName("purpur_pillar").setStrenght(1.5, 6.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: purpur stairs

    full_template.setName("end_stone_bricks").setStrenght(3., 9.).setBestTools(ToolType.PICKAXE).setMinimumToolLevel(
        1).finish()

    # missing: beetroots, grass path, end gateway, repeating command block, chain command block

    full_template.setName("frosted_ice").setSpeedMultiplier(0.98).setStrenght(.5).setDefaultModelState("age=0"). \
        setBestTools(ToolType.PICKAXE).finish()
    full_template.setName("magma_block").setStrenght(.5).setBestTools(ToolType.PICKAXE).finish()
    full_template.setName("nether_wart_block").setStrenght(1.).setBestTools(ToolType.PICKAXE).finish()
    full_template.setName("red_nether_bricks").setStrenght(2., 6.).setBestTools(ToolType.PICKAXE).finish()
    log_template.setName("bone_block").setStrenght(2.).setBestTools(ToolType.PICKAXE).finish()

    # missing: structure void, observer, colored glazed terracotta

    for color in colors:
        full_template.setName("{}_concrete".format(color)).setStrenght(1.8).setBestTools(ToolType.PICKAXE). \
            setMinimumToolLevel(1).finish()
        falling_template.setName("{}_concrete_powder".format(color)).setStrenght(.5).setBestTools(
            ToolType.SHOVEL).finish()

    # missing: kelp, kelp plant

    full_template.setName("dried_kelp_block").setStrenght(.5, 2.5).setBestTools(ToolType.AXE).finish()

    # missing: turtle egg, dead corals, corals, dead coral fans, corals fans, sea pickle

    full_template.setName("blue_ice").setStrenght(2.8).setSpeedMultiplier(1.989).setBestTools(ToolType.PICKAXE).finish()

    # missing: conduit, bamboo sapling, bamboo, potted bamboo, void air, cave air, bubble column; polished andesite,
    # diorite and granite stairs; mossy stone brick stairs, end stone brick stairs, stone stairs, smooth sandstone
    # stairs, smooth quartz stairs; granite, andesite and diorite stairs; red nether brick stairs, smooth red sandstone

    slab_template.setName("polished_granite_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("smooth_red_sandstone_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("mossy_stone_brick_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("polished_diorite_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("mossy_cobblestone_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("end_stone_brick_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("smooth_sandstone_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("smooth_quartz_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("granite_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("andesite_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("red_nether_brick_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("polished_andesite_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()
    slab_template.setName("diorite_slab").setBestTools(ToolType.PICKAXE).setMinimumToolLevel(1).finish()

    # missing: scaffolding, loom, smoker, blast furnace, cartography table, fletching table, grindstone, lectern,
    # smithing table, stonecutter, bell, lantern, campfire, sweet berry bush, structure block, jigsaw, composter, bee
    # nest, beehive, honey block, honeycomb block


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:factory_usage", load_blocks, info="loading block definitions")


@G.modloader("minecraft", "stage:combined_factory:blocks")
def combined_load():
    config = mcpython.datagen.Configuration.DataGeneratorConfig(
        "minecraft", G.local+"/resources/generated").setDefaultNamespace("minecraft")
    CombinedBlockFactory.generate_full_block_slab_wall(config, "minecraft:stone", "minecraft:block/stone",
                                                       enable=(True, True, False))
