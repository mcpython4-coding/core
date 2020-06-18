"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import mcpython.factory.ItemFactory
import globals as G
import random
from mcpython.util.enums import ToolType
import mcpython.mod.ModMcpython


def load_item():
    arrow = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:arrow").finish()
    apple = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:apple").setFoodValue(4).finish()
    baked_potato = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:baked_potato").setFoodValue(5).finish()
    beef = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:beef").setFoodValue(3).finish()
    beetroot = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:beetroot").setFoodValue(1).finish()
    beetroot_soup = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:beetroot_soup").setFoodValue(6).setMaxStackSize(
        1).finish()
    blaze_powder = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:blaze_powder").finish()
    blaze_rod = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:blaze_rod").setFuelLevel(120).finish()
    bone = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:bone").finish()
    bone_meal = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:bone_meal").finish()
    book = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:book").finish()
    bowl = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:bowl").setFuelLevel(5).finish()
    bread = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:bread").setFoodValue(5).finish()
    brick = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:brick").finish()
    broken_elytra = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:broken_elytra").finish()
    carrot = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:carrot").setFoodValue(3).finish()
    charcoal = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:charcoal").setFuelLevel(80).finish()
    chicken = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:chicken").setFoodValue(2).finish()
    chorus_fruit = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:chorus_fruit").finish()
    clay = clay_ball = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:clay_ball").finish()
    coal = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:coal").setFuelLevel(80).finish()
    cod = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cod").setFoodValue(2).finish()
    cooked_beef = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cooked_beef").setFoodValue(8).finish()
    cooked_chicken = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cooked_chicken").setFoodValue(6).finish()
    cooked_cod = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cooked_cod").setFoodValue(5).finish()
    cooked_mutton = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cooked_mutton").setFoodValue(6).finish()
    cooked_porkchop = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cooked_porkchop").setFoodValue(8).finish()
    cooked_rabbit = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cooked_rabbit").setFoodValue(5).finish()
    cooked_salmon = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cooked_salmon").setFoodValue(6).finish()
    cookie = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:cookie").setFoodValue(2).finish()
    diamond = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:diamond").finish()
    dried_kelp = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:dried_kelp").setFoodValue(1).finish()
    egg = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:egg").finish()
    emerald = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:emerald").finish()
    ender_pearl = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:ender_pearl").finish()
    ender_eye = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:ender_eye").finish()

    def lambda_add_random_xp():
        G.world.get_active_player().add_xp(random.randint(3, 11))
        return True

    experience_bottle = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:experience_bottle").setEatCallback(
        lambda_add_random_xp).setFoodValue(0).finish()
    feather = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:feather").finish()
    fermented_spider_eye = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:fermented_spider_eye").finish()
    flint = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:flint").finish()
    ghast_tear = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:ghast_tear").finish()
    glowstone_dust = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:glowstone_dust").finish()
    gold_ingot = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:gold_ingot").finish()
    gold_nugget = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:gold_nugget").finish()
    golden_apple = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:golden_apple").setFoodValue(4).finish()
    golden_carrot = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:golden_carrot").setFoodValue(6).finish()
    gunpowder = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:gunpowder").finish()
    ink_sac = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:ink_sac").finish()
    iron_ingot = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:iron_ingot").finish()
    iron_nugget = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:iron_nugget").finish()
    lapis_lazuli = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:lapis_lazuli").finish()
    leather = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:leather").finish()
    magma_cream = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:magma_cream").finish()
    melon_slice = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:melon_slice").setFoodValue(2).finish()
    mushroom_stew = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:mushroom_stew").setFoodValue(6).setMaxStackSize(
        1).finish()
    mutton = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:mutton").setFoodValue(2).finish()
    name_tag = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:name_tag").finish()
    nether_brick = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:nether_brick").finish()
    nether_star = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:nether_star").finish()
    nether_wart = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:nether_wart").finish()
    poisonous_potato = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:poisonous_potato").setFoodValue(2).finish()
    porkchop = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:porkchop").setFoodValue(3).finish()
    potato = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:potato").setFoodValue(1).finish()
    puffer_fish = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:pufferfish").setFoodValue(1).finish()
    pumpkin_pie = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:pumpkin_pie").setFoodValue(8).finish()
    quartz = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:quartz").finish()
    rabbit = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:rabbit").setFoodValue(3).finish()
    rabbit_stew = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:rabbit_stew").setFoodValue(10).setMaxStackSize(
        1).finish()
    redstone = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:redstone").finish()  # todo: binding to block
    rotten_flesh = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:rotten_flesh").setFoodValue(4).finish()
    shulker_shell = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:shulker_shell").finish()
    slime_ball = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:slime_ball").finish()
    stick = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:stick").setFuelLevel(5).finish()
    string = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:string").finish()
    sugar = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:sugar").finish()
    spider_eye = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:spider_eye").setFoodValue(2).finish()
    totem_of_undying = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:totem_of_undying").finish()
    tropical_fish = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:tropical_fish").setFoodValue(1).finish()
    wheat = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:wheat").finish()

    shears = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:shears").setToolType([ToolType.SHEAR]).setToolBrakeMutli(
        5).finish()
    for tooltype, toolname in [(ToolType.PICKAXE, "pickaxe"), (ToolType.AXE, "axe"), (ToolType.SWORD, "sword"),
                               (ToolType.HOE, "hoe"), (ToolType.SHOVEL, "shovel")]:
        mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:wooden_{}".format(toolname)).setToolType([tooltype]).\
            setToolBrakeMutli(2).setToolLevel(1).setFuelLevel(10).finish()
        mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:stone_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(4).setToolLevel(2).finish()
        mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:iron_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(6).setToolLevel(4).finish()
        mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:golden_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(8).setToolLevel(5).finish()
        mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:diamond_{}".format(toolname)).setToolType([tooltype]). \
            setToolBrakeMutli(12).setToolLevel(3).finish()

    for color in mcpython.util.enums.COLORS:
        mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:{}_dye".format(color))

    gold_helmet = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:golden_helmet").setArmorPoints(2).finish()
    gold_chestplate = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:golden_chestplate").setArmorPoints(5).finish()
    gold_leggings = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:golden_leggings").setArmorPoints(3).finish()
    gold_boots = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:golden_boots").setArmorPoints(1).finish()

    chainmail_helmet = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_helmet").setArmorPoints(2).finish()
    chainmail_chestplate = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_chestplate").setArmorPoints(5).\
        finish()
    chainmail_leggings = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_leggings").setArmorPoints(4).\
        finish()
    chainmail_boots = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:chainmail_boots").setArmorPoints(1).finish()

    iron_helmet = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:iron_helmet").setArmorPoints(2).finish()
    iron_chestplate = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:iron_chestplate").setArmorPoints(6).finish()
    iron_leggings = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:iron_leggings").setArmorPoints(5).finish()
    iron_boots = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:iron_boots").setArmorPoints(2).finish()

    diamond_helmet = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:diamond_helmet").setArmorPoints(3).finish()
    diamond_chestplate = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:diamond_chestplate").setArmorPoints(8).finish()
    diamond_leggings = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:diamond_leggings").setArmorPoints(6).finish()
    diamond_boots = mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:diamond_boots").setArmorPoints(3).finish()

    mcpython.factory.ItemFactory.ItemFactory().setName("minecraft:barrier").setHasBlockFlag(True).finish()


mcpython.mod.ModMcpython.mcpython.eventbus.subscribe("stage:item:factory_usage", load_item, info="generating items")

