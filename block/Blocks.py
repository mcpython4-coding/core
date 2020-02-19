"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import factory.BlockFactory
import globals as G
from item.ItemTool import ToolType
import mod.ModMcpython


def load_blocks():
    bedrock = factory.BlockFactory.BlockFactory().setName("minecraft:bedrock").setBrakeAbleFlag(False).finish()
    bricks = factory.BlockFactory.BlockFactory().setName("minecraft:bricks").setHardness(2).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    brick_slab = factory.BlockFactory.BlockFactory().setName("minecraft:brick_slab").setHardness(2).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()
    cobblestone = factory.BlockFactory.BlockFactory().setHardness(2).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(1).setName("minecraft:cobblestone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:coarse_dirt").finish()
    mossy_cobblestone = factory.BlockFactory.BlockFactory().setHardness(2).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(1).setName("minecraft:mossy_cobblestone").finish()
    gravel = factory.BlockFactory.BlockFactory().setName("minecraft:gravel").setHardness(0.6).setBestTools(
        [ToolType.SHOVEL]).setFallable().finish()
    red_sand = factory.BlockFactory.BlockFactory().setName("minecraft:red_sand").setHardness(0.5).setBestTools(
        [ToolType.SHOVEL]).setFallable().finish()
    sand = factory.BlockFactory.BlockFactory().setName("minecraft:sand").setHardness(0.5).setBestTools(
        [ToolType.SHOVEL]).setFallable().finish()
    stone = factory.BlockFactory.BlockFactory().setName("minecraft:stone").setHardness(1.5).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    smooth_stone = factory.BlockFactory.BlockFactory().setName("minecraft:smooth_stone").setHardness(1.5).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    stone_bricks = factory.BlockFactory.BlockFactory().setName("minecraft:stone_bricks").setHardness(1.5).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    cracked_stone_bricks = factory.BlockFactory.BlockFactory().setName("minecraft:cracked_stone_bricks").setHardness(1.5).\
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    mossy_stone_bricks = factory.BlockFactory.BlockFactory().setName("minecraft:mossy_stone_bricks").setHardness(1.5).\
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    chiseled_stone_bricks = factory.BlockFactory.BlockFactory().setName("minecraft:chiseled_stone_bricks").setHardness(
        1.5).setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    terracotta = factory.BlockFactory.BlockFactory().setName("minecraft:terracotta").setHardness(1.25).\
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:bone_block").setLog().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:bookshelf").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:obsidian").finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:ice").setSpeedMultiplier(1.4).setAllSideSolid(False).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:packed_ice").setSpeedMultiplier(1.8).setAllSideSolid(
        False).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:frosted_ice").setSpeedMultiplier(1.4).\
        setCustomModelStateFunction(lambda _: {"age": "0"}).setAllSideSolid(False).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:blue_ice").setSpeedMultiplier(2.2).setAllSideSolid(
        False).finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:pumpkin").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:carved_pumpkin").setCustomModelStateFunction(
        lambda _: {"facing": "north"}).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:melon").finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:glass").setAllSideSolid(False).finish()

    for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_concrete".format(color)).setHardness(1.8).setBestTools(
            [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_concrete_powder".format(color)).setHardness(0.5).\
            setBestTools([ToolType.SHOVEL]).setFallable().finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_wool".format(color)).setHardness(0.8).setBestTools(
            [ToolType.SHEAR]).setCustomBlockItemModification(
            lambda _, itemfactory: itemfactory.setFuelLevel(5)).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_terracotta".format(color)).setHardness(1.25).\
            setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_stained_glass".format(color)).setAllSideSolid(False).\
            finish()

    for tree in G.taghandler.taggroups["naming"].tags["#minecraft:treetypes"].entries:
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_leaves".format(tree)).setAllSideSolid(False).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_planks".format(tree)).setHardness(2).setBestTools([
            ToolType.AXE]).setCustomBlockItemModification(lambda _, itemfactory: itemfactory.setFuelLevel(15)).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_log".format(tree)).setLog().setHardness(2).\
            setBestTools([ToolType.AXE]).setCustomBlockItemModification(
            lambda _, itemfactory: itemfactory.setFuelLevel(15)).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_wood".format(tree)).setLog().setHardness(2)\
            .setBestTools([ToolType.AXE]).setCustomBlockItemModification(
            lambda _, itemfactory: itemfactory.setFuelLevel(15)).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:stripped_{}_log".format(tree)).setHardness(2).\
            setBestTools([ToolType.AXE]).setLog().setCustomBlockItemModification(
            lambda _, itemfactory: itemfactory.setFuelLevel(15)).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:stripped_{}_wood".format(tree)).setHardness(2).\
            setBestTools([ToolType.AXE]).setLog().setCustomBlockItemModification(
            lambda _, itemfactory: itemfactory.setFuelLevel(15)).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_slab".format(tree)).setSlab().setBestTools(
            [ToolType.AXE]).setHardness(2).setCustomBlockItemModification(
            lambda _, itemfactory: itemfactory.setFuelLevel(7.5)).finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:coal_block").setHardness(5).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).setCustomBlockItemModification(
        lambda _, itemfactory: itemfactory.setFuelLevel(800)).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:coal_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(1).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:diamond_block").setHardness(5).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(4).finish()  # minimum: iron
    factory.BlockFactory.BlockFactory().setName("minecraft:diamond_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(4).finish()  # minimum: iron
    factory.BlockFactory.BlockFactory().setName("minecraft:emerald_block").setHardness(5).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(4).finish()  # minimum: iron
    factory.BlockFactory.BlockFactory().setName("minecraft:emerald_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(4).finish()  # minimum: iron
    factory.BlockFactory.BlockFactory().setName("minecraft:gold_block").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(4).finish()  # minimum: iron
    factory.BlockFactory.BlockFactory().setName("minecraft:gold_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(4).finish()  # minimum: iron
    factory.BlockFactory.BlockFactory().setName("minecraft:iron_block").setHardness(5).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(2).finish()  # minimum: stone, missing: not gold
    factory.BlockFactory.BlockFactory().setName("minecraft:iron_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(2).finish()  # minimum: stone, missing: not gold
    factory.BlockFactory.BlockFactory().setName("minecraft:redstone_block").setHardness(5).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:redstone_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(4).setCustomModelStateFunction(lambda *args: {"lit": "false"}).finish()  # minimum: iron
    factory.BlockFactory.BlockFactory().setName("minecraft:quartz_block").setHardness(0.8).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:chiseled_quartz_block").setHardness(0.8).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:quartz_pillar").setHardness(0.8).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).setLog().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:smooth_quartz").setHardness(0.8).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:smooth_quartz_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:quartz_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:nether_quartz_ore").setHardness(3).setBestTools(
        [ToolType.PICKAXE]).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:lapis_block").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(2).finish()  # minimum: stone, missing: not gold
    factory.BlockFactory.BlockFactory().setName("minecraft:lapis_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(2).finish()  # minimum: stone, missing: not gold
    factory.BlockFactory.BlockFactory().setName("minecraft:clay").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:glowstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:magma_block").finish()

    for stonetype in ["granite", "andesite", "diorite"]:  # todo: move to tag
        factory.BlockFactory.BlockFactory().setName("minecraft:{}".format(stonetype)).setHardness(1.5).setBestTools(
            [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:polished_{}".format(stonetype)).setHardness(1.5).\
            setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_slab".format(stonetype)).setHardness(2).\
            setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:polished_{}_slab".format(stonetype)).setHardness(2). \
            setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:stone_slab").setHardness(2). \
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:smooth_stone_slab").setHardness(2). \
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:cobblestone_slab").setHardness(2). \
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:mossy_cobblestone_slab").setHardness(2). \
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:stone_brick_slab").setHardness(2). \
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:mossy_stone_brick_slab").setHardness(2). \
        setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).setSlab().finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:chiseled_red_sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:chiseled_sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:cut_red_sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:cut_red_sandstone_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:cut_sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:cut_sandstone_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:red_sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:red_sandstone_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:sandstone_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:smooth_red_sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:smooth_red_sandstone_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:smooth_sandstone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:smooth_sandstone_slab").setSlab().finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:dark_prismarine").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:dark_prismarine_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:prismarine").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:prismarine_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:prismarine_bricks").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:prismarine_brick_slab").setSlab().finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:dried_kelp_block").finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:end_stone").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:end_stone_brick_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:end_stone_bricks").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:purpur_block").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:purpur_pillar").setLog().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:purpur_slab").setSlab().finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:nether_brick_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:nether_bricks").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:nether_wart_block").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:netherrack").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:red_nether_brick_slab").setSlab().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:red_nether_bricks").finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:soul_sand").setSpeedMultiplier(0.5).finish()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:base", load_blocks, info="loading block definitions")

