"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
from . import Configuration
import shutil
import os
import sys

AROUND_HOLLOW = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1)]
DOWNER_ROW = [(0, 0), (1, 0), (2, 0)]
TWO_BY_TWO = [(0, 0), (1, 0), (0, 1), (1, 1)]
THREE_BY_THREE = sum([[(x, y) for y in range(3)] for x in range(3)], [])

DEFAULT_OUTPUT = G.local + "/resources/generated"  # where to output data - in dev environment

if not G.dev_environment:
    DEFAULT_OUTPUT = G.local  # when we are not in dev-environment, store them when needed in G.local


def generate_slab(config, name, base):
    config.shaped_recipe(name).setGroup("slab").setEntries(DOWNER_ROW, "minecraft:" + base).setOutput(
        (6, "minecraft:" + name))


def generate_above(config, name, base):
    config.shaped_recipe(name).setEntries([(0, 0), (0, 1)], "minecraft:" + base).setOutput("minecraft:" + name)


def generate_stair(config, name, base):
    config.shaped_recipe(name).setGroup("stair").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)], "minecraft:" + base).setOutput(
        (4, "minecraft:" + name))


def generate_wall(config, name, base):
    config.shaped_recipe(name).setGroup("wall").setEntries(
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)], "minecraft:" + base).setOutput((6, "minecraft:" + name))


def generate_wooded_recipes(config: Configuration.DataGeneratorConfig, w: str):
    config.shaped_recipe("{}_boat".format(w)).setGroup("boat").setEntries(
        [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)], "minecraft:{}_planks".format(w)).setOutput(
        "minecraft:{}_boat".format(w))
    config.shaped_recipe("{}_button".format(w)).setGroup("wooden_button").setEntry(
        0, 0, "minecraft:{}_planks".format(w)).setOutput("minecraft:{}_button".format(w))
    config.shaped_recipe("{}_door".format(w)).setGroup("wooden_door").setEntries(
        [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)], "minecraft:{}_planks".format(w)).setOutput(
        (3, "minecraft:{}_door".format(w)))
    config.shaped_recipe("{}_fence".format(w)).setGroup("wooded_fence").setEntries(
        [(0, 0), (0, 1), (2, 0), (2, 1)], "minecraft:{}_planks".format(w)).setEntries(
        [(1, 0), (1, 1)], "minecraft:stick").setOutput((3, "minecraft:{}_fence".format(w)))
    config.shaped_recipe("{}_fence_gate".format(w)).setGroup("wooded_fence").setEntries(
        [(0, 0), (0, 1), (2, 0), (2, 1)], "minecraft:stick").setEntries(
        [(1, 0), (1, 1)], "minecraft:{}_planks".format(w)).setOutput((3, "minecraft:{}_fence_gate".format(w)))
    config.shaped_recipe("{}_planks".format(w)).setEntry(0, 0, "#minecraft:{}_logs".format(w)).setOutput(
        (4, "minecraft:{}_planks".format(w))).setGroup("planks")
    config.shaped_recipe("{}_pressure_plate").setGroup("wooded_pressure_plate").setEntries(
        [(0, 0), (1, 0)], "minecraft:{}_planks".format(w)).setOutput("minecraft:{}_pressure_plate".format(w))
    config.shaped_recipe("{}_sign".format(w)).setGroup("sign").setEntries(
        [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)], "minecraft:{}_planks".format(w)).setEntry(
        1, 0, "minecraft:stick").setOutput((3, "minecraft:acacia_sign"))
    config.shaped_recipe("{}_slab".format(w)).setGroup("wooded_slab").setEntries(
        DOWNER_ROW, "minecraft:{}_planks".format(w)).setOutput((6, "minecraft:{}_slab".format(w)))
    config.shaped_recipe("{}_stairs".format(w)).setGroup("wooded_stairs").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)], "minecraft:{}_planks".format(w)).setOutput(
        (4, "minecraft:{}_stairs".format(w)))
    config.shaped_recipe("{}_trapdoor".format(w)).setGroup("wooden_trapdoor").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)], "minecraft:{}_planks".format(w)).setOutput(
        (2, "minecraft:{}_trapdoor".format(w)))
    config.shaped_recipe("{}_wood".format(w)).setGroup("bark").setEntries(
        TWO_BY_TWO, "minecraft:{}_log".format(w)).setOutput((3, "minecraft:{}_wood".format(w)))


@G.modloader("minecraft", "special:datagen:configure")
def generate_recipes():
    """
    generator for all recipes in minecraft
    """

    if "--data-gen" not in sys.argv: return  # data gen only when launched so, not when we think
    if os.path.exists(DEFAULT_OUTPUT):
        shutil.rmtree(DEFAULT_OUTPUT)
    os.makedirs(DEFAULT_OUTPUT)
    config = Configuration.DataGeneratorConfig("minecraft", G.local + "/resources/generated")

    for w in ["acacia", "birch", "oak", "jungle", "spruce", "dark_oak"]:
        generate_wooded_recipes(config, w)

    for c in ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray",
              "cyan", "blue", "purple", "green", "brown", "red", "black"]:
        config.shaped_recipe("{}_banner".format(c)).setGroup("banner").setEntries(
            [(0, 1), (0, 2), (1, 1), (1, 2), (2, 1), (2, 2)], "minecraft:{}_wool".format(c)).setEntry(
            1, 0, "minecraft:stick").setOutput("minecraft:{}_banner".format(c))
        config.shaped_recipe("{}_bed".format(c)).setGroup("bed").setEntries(
            DOWNER_ROW, "#minecraft:planks").setEntries(
            [(0, 1), (1, 1), (2, 1)], "minecraft:{}_wool".format(c)).setOutput("minecraft:{}_bed".format(c))
        config.shapeless_recipe("{}_bed_from_white_bed".format(c)).setGroup("dyed_bed").addInputs(
            ["minecraft:white_bed", "minecraft:{}_dye".format(c)]).setOutput("minecraft:{}_bed".format(c))
        config.shaped_recipe("{}_carpet".format(c)).setGroup("carpet").setEntries(
            [(0, 0), (1, 0)], "minecraft:{}_wool".format(c)).setOutput((3, "minecraft:{}_carpet".format(c)))
        config.shaped_recipe("{}_carpet_from_white_carpet".format(c)).setGroup("carpet").setEntries(
            [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)], "minecraft:white_carpet").setEntry(
            1, 1, "minecraft:{}_dye".format(c)).setOutput((8, "minecraft:{}_carpet".format(c)))
        config.shapeless_recipe("{}_concrete_powder".format(c)).addInput("minecraft:{}_dye".format(c)).addInput(
            "minecraft:sand", 4).addInput("minecraft:gravel", 4).setOutput("minecraft:{}_concrete_powder".format(c))
        config.smelting_recipe("{}_glazed_terracotta".format(c)).add_ingredient(
            "minecraft:{}_terracotta".format(c)).setOutput("minecraft:{}_glazed_terracotta".format(c)).setXp(0.1)
        config.shaped_recipe("{}_stained_glass".format(c)).setEntries(
            AROUND_HOLLOW, "minecraft:glass").setEntry(
            1, 1, "minecraft:{}_dye".format(c)).setOutput((8, "minecraft:{}_stained_glass".format(c))).setGroup(
            "stained_glass")
        config.shaped_recipe("{}_stained_glass_pane".format(c)).setEntries(
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)], "minecraft:{}_stained_glass".format(c)).setOutput(
            (16, "minecraft:{}_stained_glass_pane".format(c))).setGroup("stained_glass_pane")
        config.shaped_recipe("{}_stained_glass".format(c)).setEntries(
            AROUND_HOLLOW, "minecraft:glass_pane").setEntry(
            1, 1, "minecraft:{}_dye".format(c)).setOutput((8, "minecraft:{}_stained_glass_pane".format(c))).setGroup(
            "stained_glass_pane")
        config.shaped_recipe("{}_terracotta".format(c)).setEntries(AROUND_HOLLOW, "minecraft:terracotta").setEntry(
            1, 1, "minecraft:{}_dye".format(c)).setOutput((8, "minecraft:{}_terracotta".format(c))).setGroup(
            "stained_terracotta")
        config.shaped_recipe("{}_wool".format(c)).setEntries(AROUND_HOLLOW, "minecraft:white_wool").setEntry(
            1, 1, "minecraft:{}_dye".format(c)).setOutput((8, "minecraft:{}_wool".format(c))).setGroup("wool")

    ARMOR = ["diamond", ("iron", "minecraft:iron_ingot"), ("golden", "minecraft:gold_ingot")]
    chest = THREE_BY_THREE.copy()
    chest.remove((1, 2))
    leggings = THREE_BY_THREE.copy()
    leggings.remove((1, 0))
    leggings.remove((1, 1))
    boots = [(0, 0), (0, 1), (2, 0), (2, 1)]
    helmet = [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)]
    sticks = [(1, 0), (1, 1)]
    axe = [(0, 1), (0, 2), (1, 2)]
    hoe = [(0, 2), (1, 2)]
    pickaxe = hoe + [(2, 2)]

    for l in ARMOR:
        n = l[0] if type(l) == tuple else l
        m = l[1] if type(l) == tuple else "minecraft:" + l
        config.shaped_recipe("{}_boots".format(n)).setEntries(boots, m).setOutput("minecraft:{}_boots".format(n))
        config.shaped_recipe("{}_chestplate".format(n)).setEntries(chest, m).setOutput(
            "minecraft:{}_chestplate".format(n))
        config.shaped_recipe("{}_helmet".format(n)).setEntries(helmet, m).setOutput("minecraft:{}_helmet".format(n))
        config.shaped_recipe("{}_leggings".format(n)).setEntries(leggings, m).setOutput(
            "minecraft:{}_leggings".format(n))

    for l in ARMOR + [("wooden", "#minecraft:planks")]:
        n = l[0] if type(l) == tuple else l
        m = l[1] if type(l) == tuple else "minecraft:" + l
        config.shaped_recipe("{}_axe".format(n)).setEntries(sticks, "minecraft:stick").setEntries(
            axe, m).setOutput("minecraft:{}_axe".format(n))
        config.shaped_recipe("{}_hoe".format(n)).setEntries(sticks, "minecraft:stick").setEntries(
            hoe, m).setOutput("minecraft:{}_hoe".format(n))
        config.shaped_recipe("{}_pickaxe".format(n)).setEntries(sticks, "minecraft:stick").setEntries(
            pickaxe, m).setOutput("minecraft:{}_pickaxe".format(n))
        config.shaped_recipe("{}_shovel".format(n)).setEntries(sticks, "minecraft:stick").setEntry(
            1, 2, m).setOutput("minecraft:{}_shovel".format(n))
        config.shaped_recipe("{}_sword".format(n)).setEntry(1, 0, "minecraft:stick").setEntries(
            [(1, 1), (1, 2)], m).setOutput("minecraft:{}_sword".format(n))

    config.shaped_recipe("activator_rail").setEntries(
        [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)], "minecraft:iron_ingot").setEntries(
        [(1, 0), (1, 2)], "minecraft:stick").setEntry(1, 1, "minecraft:redstone_torch").setOutput(
        (6, "minecraft:activator_rail"))

    config.shapeless_recipe("andesite").addInputs("minecraft:diorite", "minecraft:cobblestone").setOutput(
        (2, "minecraft:andesite"))
    generate_slab(config, "andesite_slab", "andesite")
    generate_stair(config, "andesite_stairs", "andesite")
    generate_wall(config, "andesite_wall", "andesite")

    config.shaped_recipe("anvil").setEntries([(0, 2), (1, 2), (2, 2)], "minecraft:iron_block").setEntries(
        [(0, 0), (1, 0), (2, 0), (1, 1)], "minecraft:iron_ingot").setOutput("minecraft:anvil")

    config.shaped_recipe("armor_stand").setEntries(
        [(0, 0), (1, 1), (2, 0), (1, 2), (0, 2), (2, 2)], "minecraft:stick").setEntry(
        1, 0, "minecraft:smooth_stone_slab").setOutput("minecraft:armor_stand")

    config.shaped_recipe("arrow").setEntry(0, 0, "minecraft:feather").setEntry(0, 1, "minecraft:stick").setEntry(
        0, 2, "minecraft:flint").setOutput("minecraft:arrow")
    config.smelting_recipe("baked_potato").add_ingredient("minecraft:potato").setOutput("minecraft:baked_potato").setXp(
        0.35)
    config.smelting_recipe("backed_potato_from_campfire_cooking", mode="minecraft:campfire_cooking").add_ingredient(
        "minecraft:potato").setOutput("minecraft:baked_potato").setXp(0.35).setCookingTime(600)
    config.smelting_recipe("backed_potato_from_smoking", mode="minecraft:smoking").add_ingredient(
        "minecraft:potato").setOutput("minecraft:baked_potato").setXp(0.35).setCookingTime(100)

    config.shaped_recipe("barrel").setEntries(
        [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)], "#minecraft:planks").setEntries(
        [(1, 0), (1, 2)], "#minecraft:wooden_slabs").setOutput("minecraft:barrel")
    config.shaped_recipe("beacon").setEntries(DOWNER_ROW, "minecraft:obsidian").setEntries(
        [(0, 1), (0, 2), (2, 1), (2, 2), (1, 2)], "minecraft:glass").setEntry(1, 1, "minecraft:nether_start").setOutput(
        "minecraft:beacon")
    config.shaped_recipe("beehive").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 2), (1, 2), (2, 2)], "#minecraft:planks").setEntries(
        [(0, 1), (1, 1), (2, 1)], "minecraft:honeycomb").setOutput("minecraft:beehive")
    config.shapeless_recipe("beetroot_soup").addInput("minecraft:bowl").addInput("minecraft:beetroot", 6).setOutput(
        "minecraft:beetroot_soup")
    config.shapeless_recipe("back_dye").setGroup("black_dye").addInput("minecraft:ink_sac").setOutput(
        "minecraft:black_dye")
    config.shapeless_recipe("black_dye_from_wither_rose").setGroup("black_dye").addInput(
        "minecraft:wither_rose").setOutput("minecraft:black_dye")
    config.shaped_recipe("blast_furnace").setEntries(DOWNER_ROW, "minecraft:smooth_stone").setEntries(
        [(0, 1), (0, 2), (1, 2), (2, 2), (2, 1)], "minecraft:iron_ingot").setEntry(1, 1, "minecraft:furnace").setOutput(
        "minecraft:blast_furnace")
    config.shapeless_recipe("blaze_powder").addInput("minecraft:blaze_rod").setOutput((2, "minecraft:blaze_powder"))
    config.shapeless_recipe("blue_dye").addInput("minecraft:lapis_lazuli").setOutput("minecraft:blue_dye")
    config.shapeless_recipe("blue_dye_from_cornflower").addInput("minecraft:cornflower").setOutput("minecraft:blue_dye")
    config.shapeless_recipe("blue_ice").addInput("minecraft:packed_ice", 9).setOutput("minecraft:blue_ice")
    config.shapeless_recipe("bone_block").addInput("minecraft:bone_meal", 9).setOutput("minecraft:bone_block")
    config.shapeless_recipe("bone_meal").addInput("minecraft:bone").setOutput((3, "minecraft:bone_meal"))
    config.shapeless_recipe("bone_meal_from_bone_block").addInput("minecraft:bone_block").setOutput(
        (9, "minecraft:bone_meal"))
    config.shapeless_recipe("book").addInput("minecraft:paper", 3).addInput("minecraft:leather").setOutput(
        "minecraft:book")
    config.shaped_recipe("bookshelf").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 2), (1, 2), (2, 2)], "#minecraft:planks").setEntries(
        [(0, 1), (1, 1), (2, 1)], "minecraft:book").setOutput("minecraft:bookshelf")
    config.shaped_recipe("bow").setEntries(
        [(1, 0), (0, 1), (1, 2)], "minecraft:string").setEntries([(2, 0), (2, 1), (2, 2)], "minecraft:stick").setOutput(
        "minecraft:bow")
    config.shaped_recipe("bowl").setEntries([(0, 1), (1, 0), (2, 1)], "#minecraft:planks").setOutput(
        (4, "minecraft:bowl"))
    config.shaped_recipe("bread").setEntries(DOWNER_ROW, "minecraft:wheat").setOutput("minecraft:bread")
    config.shaped_recipe("brewing_stand").setEntries(DOWNER_ROW, "minecraft:cobblestone").setEntry(
        1, 1, "minecraft:blaze_rod").setOutput("minecraft:brewing_stand")
    config.smelting_recipe("brick").add_ingredient("minecraft:clay_ball").setOutput("minecraft:brick").setXp(.3)
    generate_slab(config, "brick_slab", "bricks")
    generate_stair(config, "brick_stairs", "bricks")
    generate_wall(config, "brick_wall", "bricks")
    config.shaped_recipe("bricks").setEntries(TWO_BY_TWO, "minecraft:brick").setOutput(
        "minecraft:bricks")
    config.shapeless_recipe("brown_dye").addInput("minecraft:cocoa_beans").setOutput("minecraft:brown_dye")
    config.shaped_recipe("bucket").setEntries([(0, 1), (1, 0), (2, 1)], "minecraft:iron_ingot").setOutput(
        "minecraft:bucket")
    config.shaped_recipe("cake").setEntries(DOWNER_ROW, "minecraft:wheat").setEntries(
        [(0, 1), (2, 1)], "minecraft:sugar").setEntry(1, 1, "minecraft:egg").setEntries(
        [(0, 2), (1, 2), (2, 2)], "minecraft:milk_bucket").setOutput("minecraft:cake")
    config.shaped_recipe("campfire").setEntries(DOWNER_ROW, "#minecraft:logs").setEntries(
        [(0, 1), (1, 2), (2, 1)], "minecraft:stick").setEntry(1, 1, "#minecraft:coals").setOutput("minecraft:campfire")
    config.shaped_recipe("carrot_on_a_stick").setEntry(0, 1, "minecraft:fishing_rod").setEntry(
        1, 0, "minecraft:carrot").setOutput("minecraft:carrot_on_a_stick")
    config.shaped_recipe("cartography_table").setEntries(
        [(0, 0), (1, 0), (0, 1), (1, 1)], "#minecraft:planks").setEntries(
        [(0, 2), (1, 2)], "minecraft:paper").setOutput("minecraft:cartography_table")
    config.shaped_recipe("cauldron").setEntries(
        DOWNER_ROW + [(0, 1), (0, 2), (2, 1), (2, 2)], "minecraft:iron_ingot").setOutput("minecraft:cauldron")
    config.smelting_recipe("charcoal").add_ingredient("#minecraft:logs").setOutput("minecraft:charcoal").setXp(.15)
    config.shaped_recipe("chest").setEntries(AROUND_HOLLOW, "#minecraft:planks").setOutput("minecraft:chest")
    config.shaped_recipe("chest_minecart").setEntry(0, 0, "minecraft:minecart").setEntry(
        0, 1, "minecraft:chest").setOutput("minecraft:chest_minecart")
    generate_above(config, "chiseled_quartz_block", "quartz_slab")
    generate_above(config, "chiseled_red_sandstone", "red_sandstone_slab")
    generate_above(config, "chiseled_sandstone", "sandstone_slab")
    generate_above(config, "chiseled_stone_bricks", "stone_brick_slab")
    config.shaped_recipe("clay").setEntries(TWO_BY_TWO, "minecraft:clay_ball").setOutput(
        "minecraft:clay")
    config.shaped_recipe("clock").setEntries([(1, 0), (0, 1), (2, 1), (1, 2)], "minecraft:gold_ingot").setEntry(
        1, 1, "minecraft:redstone").setOutput("minecraft:clock")
    config.shapeless_recipe("coal").addInput("minecraft:coal_block").setOutput((9, "minecraft:coal"))
    config.shapeless_recipe("coal_block").addInput("minecraft:coal", 9).setOutput("minecraft:coal_block")
    config.smelting_recipe("coal_from_blasting", "minecraft:blasting").add_ingredient("minecraft:coal_ore").setOutput(
        "minecraft:coal").setXp(.1).setCookingTime(100)
    config.smelting_recipe("coal_from_blasting").add_ingredient("minecraft:coal_ore").setOutput("minecraft:coal").setXp(
        .1)
    config.shaped_recipe("coarse_dirt").setEntries([(0, 0), (1, 1)], "minecraft:gravel").setEntries(
        [(1, 0), (0, 1)], "minecraft:dirt").setOutput((4, "minecraft:coarse_dirt"))
    generate_slab(config, "cobblestone_slab", "cobblestone")
    generate_stair(config, "cobblestone_stairs", "cobblestone")
    generate_wall(config, "cobblestone_wall", "cobblestone")
    config.shaped_recipe("comparator").setEntries(DOWNER_ROW, "minecraft:stone").setEntries(
        [(0, 1), (1, 2), (2, 1)], "minecraft:redstone_torch").setEntry(1, 1, "minecraft:quartz").setOutput(
        "minecraft:comparator")
    config.shaped_recipe("compass").setEntries([(1, 0), (0, 1), (1, 2), (2, 1)], "minecraft:iron_ingot").setEntry(
        1, 1, "minecraft:redstone").setOutput("minecraft:compass")
    config.shaped_recipe("composter").setEntries(
        DOWNER_ROW + [(0, 1), (0, 2), (2, 1), (2, 2)], "#minecraft:wooden_slabs").setOutput("minecraft:composter")
    config.shaped_recipe("conduit").setEntries(AROUND_HOLLOW, "minecraft:nautilus_shell").setEntry(
        1, 1, "minecraft:heart_of_the_sea").setOutput("minecraft:conduit")

    config.smelting_recipe("cooked_beef").add_ingredient("minecraft:beef").setOutput("minecraft:cooked_beef").setXp(.35)
    config.smelting_recipe("cooked_beef_from_campfire_cooking", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:beef").setOutput("minecraft:cooked_beef").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_beef_from_smoking", "minecraft:smoking").add_ingredient("minecraft:beef").setOutput(
        "minecraft:cooked_beef").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_chicken").add_ingredient("minecraft:chicken").setOutput(
        "minecraft:cooked_chicken").setXp(.35)
    config.smelting_recipe("cooked_chicken_from_campfire_cooking", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:chicken").setOutput("minecraft:cooked_chicken").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_chicken_from_smoking", "minecraft:smoking").add_ingredient(
        "minecraft:chicken").setOutput("minecraft:cooked_chicken").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_cod").add_ingredient("minecraft:cod").setOutput("minecraft:cooked_cod").setXp(.35)
    config.smelting_recipe("cooked_cod_from_campfire_cooking", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:cod").setOutput("minecraft:cooked_cod").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_cod_from_smoking", "minecraft:smoking").add_ingredient("minecraft:cod").setOutput(
        "minecraft:cooked_cod").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_mutton").add_ingredient("minecraft:mutton").setOutput(
        "minecraft:cooked_mutton").setXp(.35)
    config.smelting_recipe("cooked_mutton_from_campfire_cooking", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:mutton").setOutput("minecraft:cooked_mutton").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_mutton_from_smoking", "minecraft:smoking").add_ingredient(
        "minecraft:mutton").setOutput("minecraft:cooked_mutton").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_porkchop").add_ingredient("minecraft:porkchop").setOutput(
        "minecraft:cooked_porkchop").setXp(.35)
    config.smelting_recipe("cooked_porkchop_from_campfire_cooking", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:porkchop").setOutput("minecraft:cooked_porkchop").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_porkchop_from_smoking", "minecraft:smoking").add_ingredient(
        "minecraft:porkchop").setOutput("minecraft:cooked_porkchop").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_rabbit").add_ingredient("minecraft:rabbit").setOutput(
        "minecraft:cooked_rabbit").setXp(.35)
    config.smelting_recipe("cooked_rabbit_from_campfire_cooking", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:rabbit").setOutput("minecraft:cooked_rabbit").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_rabbit_from_smoking", "minecraft:smoking").add_ingredient(
        "minecraft:rabbit").setOutput("minecraft:cooked_rabbit").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_salmon").add_ingredient("minecraft:salmon").setOutput(
        "minecraft:cooked_salmon").setXp(.35)
    config.smelting_recipe("cooked_salmon_from_campfire_cooking", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:salmon").setOutput("minecraft:cooked_salmon").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_salmon_from_smoking", "minecraft:smoking").add_ingredient(
        "minecraft:salmon").setOutput("minecraft:cooked_salmon").setXp(.35).setCookingTime(100)
    
    config.shaped_recipe("cookie").setEntries([(0, 0), (2, 0)], "minecraft:wheat").setEntry(
        1, 0, "minecraft:cocoa_beans").setOutput((8, "minecraft:cookie"))
    
    config.smelting_recipe("cracked_stone_bricks").add_ingredient("minecraft:stone_bricks").setOutput(
        "minecraft:cracked_stone_bricks").setXp(.1)
    config.shaped_recipe("crafting_table").setEntries(TWO_BY_TWO, "#minecraft:planks").setOutput(
        "minecraft:crafting_table")
    config.shapeless_recipe("creeper_banner_pattern").addInputs(
        ["minecraft:paper", "minecraft:creeper_head"]).setOutput("minecraft:creeper_banner_pattern")

    config.shaped_recipe("crossbow").setEntries([(1, 0), (0, 2), (2, 2)], "minecraft:stick").setEntries(
        [(0, 1), (2, 1)], "minecraft:string").setEntry(1, 1, "minecraft:tripwire_hook").setEntry(
        1, 2, "minecraft:iron_ingot").setOutput("minecraft:crossbow")

    config.shaped_recipe("cut_red_sandstone").setEntries(TWO_BY_TWO, "minecraft:red_sandstone").setOutput(
        (4, "minecraft:cut_red_sandstone"))
    generate_slab(config, "cut_red_sandstone_slab", "cut_red_sandstone")
    config.shaped_recipe("cut_sandstone").setEntries(TWO_BY_TWO, "minecraft:sandstone").setOutput(
        "minecraft:cut_sandstone")
    generate_slab(config, "cut_sandstone_slab", "cut_sandstone")

    config.shapeless_recipe("cyan_dye").addInputs(["minecraft:blue_dye", "minecraft:green_dye"]).setOutput(
        (2, "minecraft:cyan_dye"))

    config.shaped_recipe("dark_prismarine").setEntries(AROUND_HOLLOW, "minecraft:prismarine_shard").setEntry(
        1, 1, "minecraft:black_dye").setOutput("minecraft:dark_prismarine")
    generate_slab(config, "dark_prismarine_slab", "dark_prismarine")
    generate_stair(config, "dark_prismarine_stairs", "dark_prismarine")
    config.shaped_recipe("daylight_detector").setEntries(
        DOWNER_ROW, "#minecraft:wooden_slabs").setEntries([(0, 1), (1, 1), (2, 1)], "minecraft:quartz").setEntries(
        [(0, 2), (1, 2), (2, 2)], "minecraft:glass").setOutput("minecraft:daylight_detector")
    config.shaped_recipe("detector_rail").setEntries(
        [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)], "minecraft:iron_ingot").setEntry(
        1, 0, "minecraft:redstone").setEntry(1, 1, "minecraft:stone_pressure_plate").setOutput(
        "minecraft:detector_rail")

    config.shapeless_recipe("diamond").addInput("minecraft:diamond_block").setOutput((9, "minecraft:diamond"))
    config.shapeless_recipe("diamond_block").addInput("minecraft:diamond", 9).setOutput("minecraft:diamond_block")
    config.smelting_recipe("diamond_from_blasting", "minecraft:blasting").add_ingredient(
        "minecraft:diamond_ore").setOutput("minecraft:diamond").setXp(1).setCookingTime(100)
    config.smelting_recipe("diamond_from_blasting").add_ingredient(
        "minecraft:diamond_ore").setOutput("minecraft:diamond").setXp(1)
    config.shaped_recipe("diorite").setEntries([(0, 0), (1, 1)], "minecraft:quart").setEntries(
        [(1, 0), (0, 1)], "minecraft:cobblestone").setOutput((2, "minecraft:diorite"))
    generate_slab(config, "diorite_slab", "diorite")
    generate_stair(config, "diorite_stairs", "diorite")
    generate_wall(config, "diorite_wall", "diorite")
    config.shaped_recipe("dispenser").setEntries(leggings, "minecraft:cobblestone").setEntry(
        1, 0, "minecraft:redstone").setEntry(1, 1, "minecraft:bow").setOutput("minecraft:dispenser")
    config.shapeless_recipe("died_kelp").addInput("minecraft:dried_kelp_block").setOutput(
        (9, "minecraft:dried_kelp"))
    config.shapeless_recipe("dried_kelp_block").addInput("minecraft:dried_kelp", 9).setOutput(
        "minecraft:dried_kelp_block")
    config.smelting_recipe("dried_kelp_from_smelting").add_ingredient("minecraft:kelp").setOutput(
        "minecraft:dried_kelp").setXp(.1)
    config.smelting_recipe("dried_kelp_from_smelting", "minecraft:campfire_cooking").add_ingredient(
        "minecraft:kelp").setOutput("minecraft:dried_kelp").setXp(.1).setCookingTime(600)
    config.smelting_recipe("dried_kelp_from_smelting", "minecraft:smoking").add_ingredient("minecraft:kelp").setOutput(
        "minecraft:dried_kelp").setXp(.1).setCookingTime(100)
    config.shaped_recipe("dropper").setEntries(leggings, "minecraft:cobblestone").setEntry(
        1, 0, "minecraft:redstone").setOutput("minecraft:dropper")
    config.shapeless_recipe("emerald").addInput("minecraft:emerald_block").setOutput((9, "minecraft:emerald"))
    config.shapeless_recipe("emerald_block").addInput("minecraft:emerald", 9).setOutput("minecraft:emerald_block")
    config.smelting_recipe("emerald_from_smelting").add_ingredient("minecraft:emerald_ore").setOutput(
        "minecraft:emerald").setXp(1)
    config.smelting_recipe("emerald_from_blasting").add_ingredient("minecraft:emerald_ore").setOutput(
        "minecraft:emerald").setXp(1).setCookingTime(100)
    config.shaped_recipe("enchanting_table").setEntries(DOWNER_ROW+[(1, 1)], "minecraft:obsidian").setEntries(
        [(0, 1), (2, 1)], "minecraft:diamond").setEntry(1, 2, "minecraft:book").setOutput("minecraft:enchanting_table")
    config.shaped_recipe("end_crystal").setEntries(leggings, "minecraft:glass").setEntry(
        1, 0, "minecraft:ghast_tear").setEntry(1, 1, "minecraft:ender_eye").setOutput("minecraft:end_crystal")
    config.shaped_recipe("end_rod").setEntry(0, 0, "mineceraft:popped_chorus_fruit").setEntry(
        0, 1, "minecraft:blaze_rod").setOutput((4, "minecraft:end_rod"))
    generate_slab(config, "end_stone_brick_slab", "end_stone_bricks")
    generate_stair(config, "end_stone_brick_stairs", "end_stone_bricks")
    generate_wall(config, "end_stone_brick_wall", "end_stone_bricks")
    config.shaped_recipe("end_stone_bricks").setEntries(TWO_BY_TWO, "minecraft:end_stone").setOutput(
        (4, "minecraft:end_stone_bricks"))
    config.shaped_recipe("ender_chest").setEntries(AROUND_HOLLOW, "minecraft:obsidian").setEntry(
        1, 1, "minecraft:ender_eye").setOutput("minecraft:ender_chest")
    config.shapeless_recipe("ender_eye").addInputs(["minecraft:ender_pearl", "minecraft:blaze_poweder"]).setOutput(
        "minecraft:ender_eye")
    config.shapeless_recipe("fermented_spider_eye").setOutput("minecraft:fermented_spider_eye").addInputs(
        ["minecraft:spider_eye", "minecraft:brown_mushroom", "minecraft:sugar"])
    config.shapeless_recipe("fire_charge").addInputs(["minecraft:gunpowder", "minecraft:blaze_powder", [
        "minecraft:coal", "minecraft:charcoal"]]).setOutput((3, "minecraft:fire_charge"))
    config.shaped_recipe("fishing_rod").setEntries([(0, 0), (1, 1), (2, 2)], "minecraft:stick").setEntries(
        [(2, 0), (2, 1)], "minecraft:string").setOutput("minecraft:fishing_rod")
    config.shaped_recipe("fletching_table").setEntries(TWO_BY_TWO, "#minecraft:planks").setEntries(
        [(0, 2), (1, 2)], "minecraft:flint").setOutput("minecraft:fletching_table")
    config.shapeless_recipe("flint_and_steel").addInputs(["minecraft:iron_ingot", "minecraft:flint"]).setOutput(
        "minecraft:flint_and_steel")
    config.shapeless_recipe("flower_banner_pattern").addInputs(["minecraft:paper", "minecraft:oseye_daisy"]).setOutput(
        "minecraft:flower_banner_patter")
    config.shaped_recipe("flower_pot").setEntries([(0, 1), (1, 0), (2, 1)], "minecraft:brick").setOutput(
        "minecraft:flower_pot")
    config.shaped_recipe("furnace").setEntries(AROUND_HOLLOW, "minecraft:cobblestone").setOutput("minecraft:furnace")
    config.shaped_recipe("furnace_minecart").setEntry(0, 0, "minecraft:minecart").setEntry(
        0, 1, "minecraft:furnace").setOutput("minecraft:furnace_minecart")


