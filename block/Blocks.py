"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import factory.BlockFactory
import globals as G


bedrock = factory.BlockFactory.BlockFactory().setName("minecraft:bedrock").setBrakeAbleFlag(False).finish()
brick = factory.BlockFactory.BlockFactory().setName("minecraft:bricks").finish()
cobblestone = factory.BlockFactory.BlockFactory().setName("minecraft:cobblestone")
gravel = factory.BlockFactory.BlockFactory().setName("minecraft:gravel").setFallable().finish()
red_sand = factory.BlockFactory.BlockFactory().setName("minecraft:red_sand").setFallable().finish()
sand = factory.BlockFactory.BlockFactory().setName("minecraft:sand").setFallable().finish()
stone = factory.BlockFactory.BlockFactory().setName("minecraft:stone").finish()
stone_bricks = factory.BlockFactory.BlockFactory().setName("minecraft:stone_bricks").finish()
terracotta = factory.BlockFactory.BlockFactory().setName("minecraft:terracotta").finish()

for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_concrete".format(color)).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_concrete_powder".format(color)).setFallable().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_wool".format(color)).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_terracotta".format(color)).finish()


for tree in G.taghandler.taggroups["naming"].tags["#minecraft:treetypes"].entries:
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_leaves".format(tree)).setAllSideSolid(False).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_planks".format(tree)).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_log".format(tree)).setLog().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_wood".format(tree)).setLog().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:stripped_{}_log".format(tree)).setLog().finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:stripped_{}_wood".format(tree)).setLog().finish()


for ore in G.taghandler.taggroups["naming"].tags["#minecraft:oretypes"].entries:
    if ore == "redstone":
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_ore".format(ore)).setCustomModelStateFunction(
            lambda _: {"lit": "false"}
        ).finish()
    else:
        factory.BlockFactory.BlockFactory().setName("minecraft:{}_ore".format(ore)).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:{}_block".format(ore)).finish()

for stonetype in ["granite", "andesite", "diorite"]:
    factory.BlockFactory.BlockFactory().setName("minecraft:{}".format(stonetype)).finish()
    factory.BlockFactory.BlockFactory().setName("minecraft:polished_{}".format(stonetype)).finish()

