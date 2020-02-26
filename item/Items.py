"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by fogleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import factory.ItemFactory
import globals as G
import random
from item.ItemTool import ToolType
import mod.ModMcpython


def load_item():
    arrow = factory.ItemFactory.ItemFactory().setName("minecraft:arrow").finish()
    apple = factory.ItemFactory.ItemFactory().setName("minecraft:apple").setFoodValue(4).finish()
    baked_potato = factory.ItemFactory.ItemFactory().setName("minecraft:baked_potato").setFoodValue(5).finish()
    beef = factory.ItemFactory.ItemFactory().setName("minecraft:beef").setFoodValue(3).finish()
    beetroot = factory.ItemFactory.ItemFactory().setName("minecraft:beetroot").setFoodValue(1).finish()
    beetroot_soup = factory.ItemFactory.ItemFactory().setName("minecraft:beetroot_soup").setFoodValue(6).setMaxStackSize(
        1).finish()
    blaze_powder = factory.ItemFactory.ItemFactory().setName("minecraft:blaze_powder").finish()
    blaze_rod = factory.ItemFactory.ItemFactory().setName("minecraft:blaze_rod").setFuelLevel(120).finish()
    bone = factory.ItemFactory.ItemFactory().setName("minecraft:bone").finish()
    bone_meal = factory.ItemFactory.ItemFactory().setName("minecraft:bone_meal").finish()
    book = factory.ItemFactory.ItemFactory().setName("minecraft:book").finish()
    bowl = factory.ItemFactory.ItemFactory().setName("minecraft:bowl").setFuelLevel(5).finish()
    bread = factory.ItemFactory.ItemFactory().setName("minecraft:bread").setFoodValue(5).finish()
    brick = factory.ItemFactory.ItemFactory().setName("minecraft:brick").finish()
    broken_elytra = factory.ItemFactory.ItemFactory().setName("minecraft:broken_elytra").finish()
    carrot = factory.ItemFactory.ItemFactory().setName("minecraft:carrot").setFoodValue(3).finish()
    charcoal = factory.ItemFactory.ItemFactory().setName("minecraft:charcoal").setFuelLevel(80).finish()
    chicken = factory.ItemFactory.ItemFactory().setName("minecraft:chicken").setFoodValue(2).finish()
    chorus_fruit = factory.ItemFactory.ItemFactory().setName("minecraft:chorus_fruit").finish()
    clay = clay_ball = factory.ItemFactory.ItemFactory().setName("minecraft:clay_ball").finish()
    coal = factory.ItemFactory.ItemFactory().setName("minecraft:coal").setFuelLevel(80).finish()
    cod = factory.ItemFactory.ItemFactory().setName("minecraft:cod").setFoodValue(2).finish()
    cooked_beef = factory.ItemFactory.ItemFactory().setName("minecraft:cooked_beef").setFoodValue(8).finish()
    cooked_chicken = factory.ItemFactory.ItemFactory().setName("minecraft:cooked_chicken").setFoodValue(6).finish()
    cooked_cod = factory.ItemFactory.ItemFactory().setName("minecraft:cooked_cod").setFoodValue(5).finish()
    cooked_mutton = factory.ItemFactory.ItemFactory().setName("minecraft:cooked_mutton").setFoodValue(6).finish()
    cooked_porkchop = factory.ItemFactory.ItemFactory().setName("minecraft:cooked_porkchop").setFoodValue(8).finish()
    cooked_rabbit = factory.ItemFactory.ItemFactory().setName("minecraft:cooked_rabbit").setFoodValue(5).finish()
    cooked_salmon = factory.ItemFactory.ItemFactory().setName("minecraft:cooked_salmon").setFoodValue(6).finish()
    cookie = factory.ItemFactory.ItemFactory().setName("minecraft:cookie").setFoodValue(2).finish()
    diamond = factory.ItemFactory.ItemFactory().setName("minecraft:diamond").finish()
    dried_kelp = factory.ItemFactory.ItemFactory().setName("minecraft:dried_kelp").setFoodValue(1).finish()
    egg = factory.ItemFactory.ItemFactory().setName("minecraft:egg").finish()
    emerald = factory.ItemFactory.ItemFactory().setName("minecraft:emerald").finish()
    ender_pearl = factory.ItemFactory.ItemFactory().setName("minecraft:ender_pearl").finish()
    ender_eye = factory.ItemFactory.ItemFactory().setName("minecraft:ender_eye").finish()

    def lambda_add_random_xp():
        G.player.add_xp(random.randint(3, 11))
        return True

    experience_bottle = factory.ItemFactory.ItemFactory().setName("minecraft:experience_bottle").setEatCallback(
        lambda_add_random_xp).setFoodValue(0).finish()
    feather = factory.ItemFactory.ItemFactory().setName("minecraft:feather").finish()
    fermented_spider_eye = factory.ItemFactory.ItemFactory().setName("minecraft:fermented_spider_eye").finish()
    flint = factory.ItemFactory.ItemFactory().setName("minecraft:flint").finish()
    ghast_tear = factory.ItemFactory.ItemFactory().setName("minecraft:ghast_tear").finish()
    glowstone_dust = factory.ItemFactory.ItemFactory().setName("minecraft:glowstone_dust").finish()
    gold_ingot = factory.ItemFactory.ItemFactory().setName("minecraft:gold_ingot").finish()
    gold_nugget = factory.ItemFactory.ItemFactory().setName("minecraft:gold_nugget").finish()
    golden_apple = factory.ItemFactory.ItemFactory().setName("minecraft:golden_apple").setFoodValue(4).finish()
    golden_carrot = factory.ItemFactory.ItemFactory().setName("minecraft:golden_carrot").setFoodValue(6).finish()
    gunpowder = factory.ItemFactory.ItemFactory().setName("minecraft:gunpowder").finish()
    ink_sac = factory.ItemFactory.ItemFactory().setName("minecraft:ink_sac").finish()
    iron_ingot = factory.ItemFactory.ItemFactory().setName("minecraft:iron_ingot").finish()
    iron_nugget = factory.ItemFactory.ItemFactory().setName("minecraft:iron_nugget").finish()
    lapis_lazuli = factory.ItemFactory.ItemFactory().setName("minecraft:lapis_lazuli").finish()
    leather = factory.ItemFactory.ItemFactory().setName("minecraft:leather").finish()
    magma_cream = factory.ItemFactory.ItemFactory().setName("minecraft:magma_cream").finish()
    melon_slice = factory.ItemFactory.ItemFactory().setName("minecraft:melon_slice").setFoodValue(2).finish()
    mushroom_stew = factory.ItemFactory.ItemFactory().setName("minecraft:mushroom_stew").setFoodValue(6).setMaxStackSize(
        1).finish()
    mutton = factory.ItemFactory.ItemFactory().setName("minecraft:mutton").setFoodValue(2).finish()
    name_tag = factory.ItemFactory.ItemFactory().setName("minecraft:name_tag").finish()
    nether_brick = factory.ItemFactory.ItemFactory().setName("minecraft:nether_brick").finish()
    nether_star = factory.ItemFactory.ItemFactory().setName("minecraft:nether_star").finish()
    nether_wart = factory.ItemFactory.ItemFactory().setName("minecraft:nether_wart").finish()
    poisonous_potato = factory.ItemFactory.ItemFactory().setName("minecraft:poisonous_potato").setFoodValue(2).finish()
    porkchop = factory.ItemFactory.ItemFactory().setName("minecraft:porkchop").setFoodValue(3).finish()
    potato = factory.ItemFactory.ItemFactory().setName("minecraft:potato").setFoodValue(1).finish()
    puffer_fish = factory.ItemFactory.ItemFactory().setName("minecraft:pufferfish").setFoodValue(1).finish()
    pumpkin_pie = factory.ItemFactory.ItemFactory().setName("minecraft:pumpkin_pie").setFoodValue(8).finish()
    quartz = factory.ItemFactory.ItemFactory().setName("minecraft:quartz").finish()
    rabbit = factory.ItemFactory.ItemFactory().setName("minecraft:rabbit").setFoodValue(3).finish()
    rabbit_stew = factory.ItemFactory.ItemFactory().setName("minecraft:rabbit_stew").setFoodValue(10).setMaxStackSize(
        1).finish()
    redstone = factory.ItemFactory.ItemFactory().setName("minecraft:redstone").finish()  # todo: binding to block
    rotten_flesh = factory.ItemFactory.ItemFactory().setName("minecraft:rotten_flesh").setFoodValue(4).finish()
    shulker_shell = factory.ItemFactory.ItemFactory().setName("minecraft:shulker_shell").finish()
    slime_ball = factory.ItemFactory.ItemFactory().setName("minecraft:slime_ball").finish()
    stick = factory.ItemFactory.ItemFactory().setName("minecraft:stick").setFuelLevel(5).finish()
    string = factory.ItemFactory.ItemFactory().setName("minecraft:string").finish()
    sugar = factory.ItemFactory.ItemFactory().setName("minecraft:sugar").finish()
    spider_eye = factory.ItemFactory.ItemFactory().setName("minecraft:spider_eye").setFoodValue(2).finish()
    totem_of_undying = factory.ItemFactory.ItemFactory().setName("minecraft:totem_of_undying").finish()
    tropical_fish = factory.ItemFactory.ItemFactory().setName("minecraft:tropical_fish").setFoodValue(1).finish()
    wheat = factory.ItemFactory.ItemFactory().setName("minecraft:wheat").finish()

    shears = factory.ItemFactory.ItemFactory().setName("minecraft:shears").setToolType([ToolType.SHEAR]).setToolBrakeMutli(
        5).finish()
    for tooltype, toolname in [(ToolType.PICKAXE, "pickaxe"), (ToolType.AXE, "axe"), (ToolType.SWORD, "sword"),
                               (ToolType.HOE, "hoe"), (ToolType.SHOVEL, "shovel")]:
        factory.ItemFactory.ItemFactory().setName("minecraft:wooden_{}".format(toolname)).setToolType([tooltype]).\
            setToolBrakeMutli(2).setToolLevel(1).setFuelLevel(10).finish()
        factory.ItemFactory.ItemFactory().setName("minecraft:stone_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(4).setToolLevel(2).finish()
        factory.ItemFactory.ItemFactory().setName("minecraft:iron_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(6).setToolLevel(4).finish()
        factory.ItemFactory.ItemFactory().setName("minecraft:golden_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(8).setToolLevel(5).finish()
        factory.ItemFactory.ItemFactory().setName("minecraft:diamond_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(12).setToolLevel(3).finish()

    for color in G.taghandler.taggroups["naming"].tags["#minecraft:colors"].entries:
        factory.ItemFactory.ItemFactory().setName("minecraft:{}_dye".format(color))

    gold_helmet = factory.ItemFactory.ItemFactory().setName("minecraft:golden_helmet").setArmorPoints(2).finish()
    gold_chestplate = factory.ItemFactory.ItemFactory().setName("minecraft:golden_chestplate").setArmorPoints(5).finish()
    gold_leggings = factory.ItemFactory.ItemFactory().setName("minecraft:golden_leggings").setArmorPoints(3).finish()
    gold_boots = factory.ItemFactory.ItemFactory().setName("minecraft:golden_boots").setArmorPoints(1).finish()

    chainmail_helmet = factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_helmet").setArmorPoints(2).finish()
    chainmail_chestplate = factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_chestplate").setArmorPoints(5).\
        finish()
    chainmail_leggings = factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_leggings").setArmorPoints(4).\
        finish()
    chainmail_boots = factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_boots").setArmorPoints(1).finish()

    iron_helmet = factory.ItemFactory.ItemFactory().setName("minecraft:iron_helmet").setArmorPoints(2).finish()
    iron_chestplate = factory.ItemFactory.ItemFactory().setName("minecraft:iron_chestplate").setArmorPoints(6).finish()
    iron_leggings = factory.ItemFactory.ItemFactory().setName("minecraft:iron_leggings").setArmorPoints(5).finish()
    iron_boots = factory.ItemFactory.ItemFactory().setName("minecraft:iron_boots").setArmorPoints(2).finish()

    diamond_helmet = factory.ItemFactory.ItemFactory().setName("minecraft:diamond_helmet").setArmorPoints(3).finish()
    diamond_chestplate = factory.ItemFactory.ItemFactory().setName("minecraft:diamond_chestplate").setArmorPoints(8).finish()
    diamond_leggings = factory.ItemFactory.ItemFactory().setName("minecraft:diamond_leggings").setArmorPoints(6).finish()
    diamond_boots = factory.ItemFactory.ItemFactory().setName("minecraft:diamond_boots").setArmorPoints(3).finish()


mod.ModMcpython.mcpython.eventbus.subscribe("stage:item:base", load_item, info="generating items")

