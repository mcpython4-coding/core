"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import factory.BlockFactory
import globals as G
from item.ItemTool import ToolType
import mod.ModMcpython


def load_blocks():
    bedrock = factory.BlockFactory.BlockFactory().setName("minecraft:bedrock").setBrakeAbleFlag(False).finish()
    bricks = factory.BlockFactory.BlockFactory().setName("minecraft:bricks").setHardness(2).setBestTools(
        [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
    cobblestone = factory.BlockFactory.BlockFactory().setHardness(2).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(1).setName("minecraft:cobblestone")
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

    for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_concrete".format(color)).setHardness(1.8).setBestTools(
            [ToolType.PICKAXE]).setMinimumToolLevel(1).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_concrete_powder".format(color)).setHardness(0.5).\
            setBestTools([ToolType.SHOVEL]).setFallable().finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_wool".format(color)).setHardness(0.8).setBestTools(
            [ToolType.SHEAR]).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_terracotta".format(color)).setHardness(1.25).\
            setBestTools([ToolType.PICKAXE]).setMinimumToolLevel(1).finish()

    for tree in G.taghandler.taggroups["naming"].tags["#minecraft:treetypes"].entries:
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_leaves".format(tree)).setAllSideSolid(False).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_planks".format(tree)).setHardness(2).setBestTools([
            ToolType.AXE]).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_log".format(tree)).setLog().setHardness(2).setBestTools([
            ToolType.AXE]).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_wood".format(tree)).setLog().setHardness(2).setBestTools([
            ToolType.AXE]).finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:stripped_{}_log".format(tree)).setHardness(2).setBestTools([
            ToolType.AXE]).setLog().finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:stripped_{}_wood".format(tree)).setHardness(2).setBestTools([
            ToolType.AXE]).setLog().finish()
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_slab".format(tree)).setSlab().setBestTools(
            [ToolType.AXE]).setHardness(2).finish()

    factory.BlockFactory.BlockFactory().setName("minecraft:coal_block").setHardness(5).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(1).finish()
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
    factory.BlockFactory.BlockFactory().setName("minecraft:nether_quartz_ore").setHardness(3).setBestTools(
        [ToolType.PICKAXE]).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:lapis_block").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(2).finish()  # minimum: stone, missing: not gold
    factory.BlockFactory.BlockFactory().setName("minecraft:lapis_ore").setHardness(3).setBestTools([ToolType.PICKAXE]).\
        setMinimumToolLevel(2).finish()  # minimum: stone, missing: not gold

    for stonetype in ["granite", "andesite", "diorite"]:
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


mod.ModMcpython.mcpython.eventbus.subscribe("stage:block:base", load_blocks, info="loading block definitions")

