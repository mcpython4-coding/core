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

TWO_BY_TWO = sum([[(x, y) for y in range(2)] for x in range(2)], [])
THREE_BY_THREE = sum([[(x, y) for y in range(3)] for x in range(3)], [])
THREE_BY_TWO = sum([[(x, y) for y in range(2)] for x in range(3)], [])
TWO_BY_THREE = sum([[(x, y) for y in range(3)] for x in range(2)], [])
STAIR = [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

DOWNER_ROW = [(x, 0) for x in range(3)]

SMALL_V = [(0, 1), (1, 0), (2, 1)]
SMALL_U = THREE_BY_TWO.copy()
SMALL_U.remove((1, 1))
AROUND_HOLLOW = THREE_BY_THREE.copy()
AROUND_HOLLOW.remove((1, 1))

DEFAULT_OUTPUT = G.local + "/resources/generated"  # where to output data - in dev environment

if not G.dev_environment:
    DEFAULT_OUTPUT = G.local  # when we are not in dev-environment, store them when needed in G.local


def generate_slab(config, name, base):
    config.shaped_recipe(name).setGroup("slab").setEntries(DOWNER_ROW, base).setOutput((6, name))


def generate_above(config, name, base):
    config.shaped_recipe(name).setEntries([(0, 0), (0, 1)], base).setOutput(name)


def generate_stair(config, name, base):
    config.shaped_recipe(name).setGroup("stair").setEntries(STAIR, base).setOutput((4, name))


def generate_wall(config, name, base):
    config.shaped_recipe(name).setGroup("wall").setEntries(THREE_BY_TWO, "" + base).setOutput((6, "" + name))


def generate_wooded_recipes(config: Configuration.DataGeneratorConfig, w: str):
    config.shaped_recipe("{}_boat".format(w)).setGroup("boat").setEntries(SMALL_U, "{}_planks".format(w)).setOutput(
        "{}_boat".format(w))
    config.shaped_recipe("{}_button".format(w)).setGroup("wooden_button").setEntry(
        0, 0, "{}_planks".format(w)).setOutput("{}_button".format(w))
    config.shaped_recipe("{}_door".format(w)).setGroup("wooden_door").setEntries(
        TWO_BY_THREE, "{}_planks".format(w)).setOutput((3, "{}_door".format(w)))
    config.shaped_recipe("{}_fence".format(w)).setGroup("wooded_fence").setEntries(
        [(0, 0), (0, 1), (2, 0), (2, 1)], "{}_planks".format(w)).setEntries([(1, 0), (1, 1)], "stick").setOutput(
        (3, "{}_fence".format(w)))
    config.shaped_recipe("{}_fence_gate".format(w)).setGroup("wooded_fence").setEntries(
        [(0, 0), (0, 1), (2, 0), (2, 1)], "stick").setEntries([(1, 0), (1, 1)], "{}_planks".format(w)).setOutput(
        (3, "{}_fence_gate".format(w)))
    config.shaped_recipe("{}_planks".format(w)).setEntry(0, 0, "#{}_logs".format(w)).setOutput(
        (4, "{}_planks".format(w))).setGroup("planks")
    config.shaped_recipe("{}_pressure_plate").setGroup("wooded_pressure_plate").setEntries(
        [(0, 0), (1, 0)], "{}_planks".format(w)).setOutput("{}_pressure_plate".format(w))
    config.shaped_recipe("{}_sign".format(w)).setGroup("sign").setEntries(
        [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)], "{}_planks".format(w)).setEntry(1, 0, "stick").setOutput(
        (3, "acacia_sign"))
    config.shaped_recipe("{}_slab".format(w)).setGroup("wooded_slab").setEntries(
        DOWNER_ROW, "{}_planks".format(w)).setOutput((6, "{}_slab".format(w)))
    config.shaped_recipe("{}_stairs".format(w)).setGroup("wooded_stairs").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)], "{}_planks".format(w)).setOutput((4, "{}_stairs".format(w)))
    config.shaped_recipe("{}_trapdoor".format(w)).setGroup("wooden_trapdoor").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)], "{}_planks".format(w)).setOutput((2, "{}_trapdoor".format(w)))
    config.shaped_recipe("{}_wood".format(w)).setGroup("bark").setEntries(
        TWO_BY_TWO, "{}_log".format(w)).setOutput((3, "{}_wood".format(w)))


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
    config.setDefaultNamespace("minecraft")

    for w in ["acacia", "birch", "oak", "jungle", "spruce", "dark_oak"]:
        generate_wooded_recipes(config, w)

    for c in ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray",
              "cyan", "blue", "purple", "green", "brown", "red", "black"]:
        config.shaped_recipe("{}_banner".format(c)).setGroup("banner").setEntries(
            [(e[0], e[1]+1) for e in THREE_BY_TWO], "{}_wool".format(c)).setEntry(1, 0, "stick").setOutput(
            "{}_banner".format(c))
        config.shaped_recipe("{}_bed".format(c)).setGroup("bed").setEntries(DOWNER_ROW, "#planks").setEntries(
            [(0, 1), (1, 1), (2, 1)], "{}_wool".format(c)).setOutput("{}_bed".format(c))
        config.shapeless_recipe("{}_bed_from_white_bed".format(c)).setGroup("dyed_bed").addInputs(
            ["white_bed", "{}_dye".format(c)]).setOutput("{}_bed".format(c))
        config.shaped_recipe("{}_carpet".format(c)).setGroup("carpet").setEntries(
            [(0, 0), (1, 0)], "{}_wool".format(c)).setOutput((3, "{}_carpet".format(c)))
        config.shaped_recipe("{}_carpet_from_white_carpet".format(c)).setGroup("carpet").setEntries(
            AROUND_HOLLOW, "white_carpet").setEntry(1, 1, "{}_dye".format(c)).setOutput((8, "{}_carpet".format(c)))
        config.shapeless_recipe("{}_concrete_powder".format(c)).addInput("{}_dye".format(c)).addInput(
            "sand", 4).addInput("gravel", 4).setOutput("{}_concrete_powder".format(c))
        config.smelting_recipe("{}_glazed_terracotta".format(c)).add_ingredient("{}_terracotta".format(c)).setOutput(
            "{}_glazed_terracotta".format(c)).setXp(0.1)
        config.shaped_recipe("{}_stained_glass".format(c)).setEntries(AROUND_HOLLOW, "glass").setEntry(
            1, 1, "{}_dye".format(c)).setOutput((8, "{}_stained_glass".format(c))).setGroup("stained_glass")
        config.shaped_recipe("{}_stained_glass_pane".format(c)).setEntries(
            THREE_BY_TWO, "{}_stained_glass".format(c)).setOutput((16, "{}_stained_glass_pane".format(c))).setGroup(
            "stained_glass_pane")
        config.shaped_recipe("{}_stained_glass".format(c)).setEntries(AROUND_HOLLOW, "glass_pane").setEntry(
            1, 1, "{}_dye".format(c)).setOutput((8, "{}_stained_glass_pane".format(c))).setGroup("stained_glass_pane")
        config.shaped_recipe("{}_terracotta".format(c)).setEntries(AROUND_HOLLOW, "terracotta").setEntry(
            1, 1, "{}_dye".format(c)).setOutput((8, "{}_terracotta".format(c))).setGroup("stained_terracotta")
        config.shaped_recipe("{}_wool".format(c)).setEntries(AROUND_HOLLOW, "white_wool").setEntry(
            1, 1, "{}_dye".format(c)).setOutput((8, "{}_wool".format(c))).setGroup("wool")

    ARMOR = ["diamond", ("iron", "iron_ingot"), ("golden", "gold_ingot")]
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
        m = l[1] if type(l) == tuple else "" + l
        config.shaped_recipe("{}_boots".format(n)).setEntries(boots, m).setOutput("{}_boots".format(n))
        config.shaped_recipe("{}_chestplate".format(n)).setEntries(chest, m).setOutput("{}_chestplate".format(n))
        config.shaped_recipe("{}_helmet".format(n)).setEntries(helmet, m).setOutput("{}_helmet".format(n))
        config.shaped_recipe("{}_leggings".format(n)).setEntries(leggings, m).setOutput("{}_leggings".format(n))

    for l in ARMOR + [("wooden", "#planks")]:
        n = l[0] if type(l) == tuple else l
        m = l[1] if type(l) == tuple else "" + l
        config.shaped_recipe("{}_axe".format(n)).setEntries(sticks, "stick").setEntries(axe, m).setOutput(
            "{}_axe".format(n))
        config.shaped_recipe("{}_hoe".format(n)).setEntries(sticks, "stick").setEntries(hoe, m).setOutput(
            "{}_hoe".format(n))
        config.shaped_recipe("{}_pickaxe".format(n)).setEntries(sticks, "stick").setEntries(pickaxe, m).setOutput(
            "{}_pickaxe".format(n))
        config.shaped_recipe("{}_shovel".format(n)).setEntries(sticks, "stick").setEntry(1, 2, m).setOutput(
            "{}_shovel".format(n))
        config.shaped_recipe("{}_sword".format(n)).setEntry(1, 0, "stick").setEntries([(1, 1), (1, 2)], m).setOutput(
            "{}_sword".format(n))

    config.shaped_recipe("activator_rail").setEntries(
        [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)], "iron_ingot").setEntries([(1, 0), (1, 2)], "stick").setEntry(
        1, 1, "redstone_torch").setOutput((6, "activator_rail"))

    config.shapeless_recipe("andesite").addInputs("diorite", "cobblestone").setOutput((2, "andesite"))
    generate_slab(config, "andesite_slab", "andesite")
    generate_stair(config, "andesite_stairs", "andesite")
    generate_wall(config, "andesite_wall", "andesite")

    config.shaped_recipe("anvil").setEntries([(0, 2), (1, 2), (2, 2)], "iron_block").setEntries(
        [(0, 0), (1, 0), (2, 0), (1, 1)], "iron_ingot").setOutput("anvil")

    config.shaped_recipe("armor_stand").setEntries([(0, 0), (1, 1), (2, 0), (1, 2), (0, 2), (2, 2)], "stick").setEntry(
        1, 0, "smooth_stone_slab").setOutput("armor_stand")

    config.shaped_recipe("arrow").setEntry(0, 0, "feather").setEntry(0, 1, "stick").setEntry(0, 2, "flint").setOutput(
        "arrow")
    config.smelting_recipe("baked_potato").add_ingredient("potato").setOutput("baked_potato").setXp(0.35)
    config.smelting_recipe("backed_potato_from_campfire_cooking", mode="campfire_cooking").add_ingredient(
        "potato").setOutput("baked_potato").setXp(0.35).setCookingTime(600)
    config.smelting_recipe("backed_potato_from_smoking", mode="minecraft:smoking").add_ingredient("potato").setOutput(
        "baked_potato").setXp(0.35).setCookingTime(100)

    config.shaped_recipe("barrel").setEntries([(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)], "#planks").setEntries(
        [(1, 0), (1, 2)], "#wooden_slabs").setOutput("barrel")
    config.shaped_recipe("beacon").setEntries(DOWNER_ROW, "obsidian").setEntries(
        [(0, 1), (0, 2), (2, 1), (2, 2), (1, 2)], "glass").setEntry(1, 1, "nether_start").setOutput("beacon")
    config.shaped_recipe("beehive").setEntries([(0, 0), (1, 0), (2, 0), (0, 2), (1, 2), (2, 2)], "#planks").setEntries(
        [(0, 1), (1, 1), (2, 1)], "honeycomb").setOutput("beehive")
    config.shapeless_recipe("beetroot_soup").addInput("bowl").addInput("beetroot", 6).setOutput("beetroot_soup")
    config.shapeless_recipe("back_dye").setGroup("black_dye").addInput("ink_sac").setOutput("black_dye")
    config.shapeless_recipe("black_dye_from_wither_rose").setGroup("black_dye").addInput("wither_rose").setOutput(
        "black_dye")
    config.shaped_recipe("blast_furnace").setEntries(DOWNER_ROW, "smooth_stone").setEntries(
        [(0, 1), (0, 2), (1, 2), (2, 2), (2, 1)], "iron_ingot").setEntry(1, 1, "furnace").setOutput("blast_furnace")
    config.shapeless_recipe("blaze_powder").addInput("blaze_rod").setOutput((2, "blaze_powder"))
    config.shapeless_recipe("blue_dye").addInput("lapis_lazuli").setOutput("blue_dye")
    config.shapeless_recipe("blue_dye_from_cornflower").addInput("cornflower").setOutput("blue_dye")
    config.shaped_recipe("blue_ice").setEntries(THREE_BY_THREE, "packed_ice").setOutput("blue_ice")
    config.shaped_recipe("bone_block").setEntries(THREE_BY_THREE, "bone_meal").setOutput("bone_block")
    config.shapeless_recipe("bone_meal").addInput("bone").setOutput((3, "bone_meal"))
    config.shapeless_recipe("bone_meal_from_bone_block").addInput("bone_block").setOutput((9, "bone_meal"))
    config.shapeless_recipe("book").addInput("paper", 3).addInput("leather").setOutput("book")
    config.shaped_recipe("bookshelf").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 2), (1, 2), (2, 2)], "#planks").setEntries(
        [(0, 1), (1, 1), (2, 1)], "book").setOutput("bookshelf")
    config.shaped_recipe("bow").setEntries(
        [(1, 0), (0, 1), (1, 2)], "string").setEntries([(2, 0), (2, 1), (2, 2)], "stick").setOutput("bow")
    config.shaped_recipe("bowl").setEntries(SMALL_V, "#planks").setOutput((4, "bowl"))
    config.shaped_recipe("bread").setEntries(DOWNER_ROW, "wheat").setOutput("bread")
    config.shaped_recipe("brewing_stand").setEntries(DOWNER_ROW, "cobblestone").setEntry(1, 1, "blaze_rod").setOutput(
        "brewing_stand")
    config.smelting_recipe("brick").add_ingredient("clay_ball").setOutput("brick").setXp(.3)
    generate_slab(config, "brick_slab", "bricks")
    generate_stair(config, "brick_stairs", "bricks")
    generate_wall(config, "brick_wall", "bricks")
    config.shaped_recipe("bricks").setEntries(TWO_BY_TWO, "brick").setOutput("bricks")
    config.shapeless_recipe("brown_dye").addInput("cocoa_beans").setOutput("brown_dye")
    config.shaped_recipe("bucket").setEntries(SMALL_V, "iron_ingot").setOutput("bucket")
    config.shaped_recipe("cake").setEntries(DOWNER_ROW, "wheat").setEntries([(0, 1), (2, 1)], "sugar").setEntry(
        1, 1, "egg").setEntries([(0, 2), (1, 2), (2, 2)], "milk_bucket").setOutput("cake")
    config.shaped_recipe("campfire").setEntries(DOWNER_ROW, "#logs").setEntries(
        [(0, 1), (1, 2), (2, 1)], "stick").setEntry(1, 1, "#coals").setOutput("campfire")
    config.shaped_recipe("carrot_on_a_stick").setEntry(0, 1, "fishing_rod").setEntry(1, 0, "carrot").setOutput(
        "carrot_on_a_stick")
    config.shaped_recipe("cartography_table").setEntries([(0, 0), (1, 0), (0, 1), (1, 1)], "#planks").setEntries(
        [(0, 2), (1, 2)], "paper").setOutput("cartography_table")
    config.shaped_recipe("cauldron").setEntries(DOWNER_ROW + [(0, 1), (0, 2), (2, 1), (2, 2)], "iron_ingot").setOutput(
        "cauldron")
    config.smelting_recipe("charcoal").add_ingredient("#logs").setOutput("charcoal").setXp(.15)
    config.shaped_recipe("chest").setEntries(AROUND_HOLLOW, "#planks").setOutput("chest")
    config.shaped_recipe("chest_minecart").setEntry(0, 0, "minecart").setEntry(0, 1, "chest").setOutput(
        "chest_minecart")
    generate_above(config, "chiseled_quartz_block", "quartz_slab")
    generate_above(config, "chiseled_red_sandstone", "red_sandstone_slab")
    generate_above(config, "chiseled_sandstone", "sandstone_slab")
    generate_above(config, "chiseled_stone_bricks", "stone_brick_slab")
    config.shaped_recipe("clay").setEntries(TWO_BY_TWO, "clay_ball").setOutput("clay")
    config.shaped_recipe("clock").setEntries([(1, 0), (0, 1), (2, 1), (1, 2)], "gold_ingot").setEntry(
        1, 1, "redstone").setOutput("clock")
    config.shapeless_recipe("coal").addInput("coal_block").setOutput((9, "coal"))
    config.shaped_recipe("coal_block").setEntries(THREE_BY_THREE, "coal").setOutput("coal_block")
    config.smelting_recipe("coal_from_blasting", "minecraft:blasting").add_ingredient("coal_ore").setOutput("coal").setXp(
        .1).setCookingTime(100)
    config.smelting_recipe("coal_from_blasting").add_ingredient("coal_ore").setOutput("coal").setXp(.1)
    config.shaped_recipe("coarse_dirt").setEntries([(0, 0), (1, 1)], "gravel").setEntries(
        [(1, 0), (0, 1)], "dirt").setOutput((4, "coarse_dirt"))
    generate_slab(config, "cobblestone_slab", "cobblestone")
    generate_stair(config, "cobblestone_stairs", "cobblestone")
    generate_wall(config, "cobblestone_wall", "cobblestone")
    config.shaped_recipe("comparator").setEntries(DOWNER_ROW, "stone").setEntries(
        [(0, 1), (1, 2), (2, 1)], "redstone_torch").setEntry(1, 1, "quartz").setOutput("comparator")
    config.shaped_recipe("compass").setEntries([(1, 0), (0, 1), (1, 2), (2, 1)], "iron_ingot").setEntry(
        1, 1, "redstone").setOutput("compass")
    config.shaped_recipe("composter").setEntries(
        DOWNER_ROW + [(0, 1), (0, 2), (2, 1), (2, 2)], "#wooden_slabs").setOutput("composter")
    config.shaped_recipe("conduit").setEntries(AROUND_HOLLOW, "nautilus_shell").setEntry(
        1, 1, "heart_of_the_sea").setOutput("conduit")

    config.smelting_recipe("cooked_beef").add_ingredient("beef").setOutput("cooked_beef").setXp(.35)
    config.smelting_recipe("cooked_beef_from_campfire_cooking", "campfire_cooking").add_ingredient(
        "beef").setOutput("cooked_beef").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_beef_from_smoking", "minecraft:smoking").add_ingredient("beef").setOutput(
        "cooked_beef").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_chicken").add_ingredient("chicken").setOutput(
        "cooked_chicken").setXp(.35)
    config.smelting_recipe("cooked_chicken_from_campfire_cooking", "campfire_cooking").add_ingredient(
        "chicken").setOutput("cooked_chicken").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_chicken_from_smoking", "minecraft:smoking").add_ingredient("chicken").setOutput(
        "cooked_chicken").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_cod").add_ingredient("cod").setOutput("cooked_cod").setXp(.35)
    config.smelting_recipe("cooked_cod_from_campfire_cooking", "campfire_cooking").add_ingredient("cod").setOutput(
        "cooked_cod").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_cod_from_smoking", "minecraft:smoking").add_ingredient("cod").setOutput("cooked_cod").setXp(
        .35).setCookingTime(100)

    config.smelting_recipe("cooked_mutton").add_ingredient("mutton").setOutput("cooked_mutton").setXp(.35)
    config.smelting_recipe("cooked_mutton_from_campfire_cooking", "campfire_cooking").add_ingredient(
        "mutton").setOutput("cooked_mutton").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_mutton_from_smoking", "minecraft:smoking").add_ingredient("mutton").setOutput(
        "cooked_mutton").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_porkchop").add_ingredient("porkchop").setOutput("cooked_porkchop").setXp(.35)
    config.smelting_recipe("cooked_porkchop_from_campfire_cooking", "campfire_cooking").add_ingredient(
        "porkchop").setOutput("cooked_porkchop").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_porkchop_from_smoking", "minecraft:smoking").add_ingredient("porkchop").setOutput(
        "cooked_porkchop").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_rabbit").add_ingredient("rabbit").setOutput("cooked_rabbit").setXp(.35)
    config.smelting_recipe("cooked_rabbit_from_campfire_cooking", "campfire_cooking").add_ingredient(
        "rabbit").setOutput("cooked_rabbit").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_rabbit_from_smoking", "minecraft:smoking").add_ingredient("rabbit").setOutput(
        "cooked_rabbit").setXp(.35).setCookingTime(100)

    config.smelting_recipe("cooked_salmon").add_ingredient("salmon").setOutput("cooked_salmon").setXp(.35)
    config.smelting_recipe("cooked_salmon_from_campfire_cooking", "campfire_cooking").add_ingredient(
        "salmon").setOutput("cooked_salmon").setXp(.35).setCookingTime(600)
    config.smelting_recipe("cooked_salmon_from_smoking", "minecraft:smoking").add_ingredient(
        "salmon").setOutput("cooked_salmon").setXp(.35).setCookingTime(100)

    config.shaped_recipe("cookie").setEntries([(0, 0), (2, 0)], "wheat").setEntry(1, 0, "cocoa_beans").setOutput(
        (8, "cookie"))

    config.smelting_recipe("cracked_stone_bricks").add_ingredient("stone_bricks").setOutput(
        "cracked_stone_bricks").setXp(.1)
    config.shaped_recipe("crafting_table").setEntries(TWO_BY_TWO, "#planks").setOutput("crafting_table")
    config.shapeless_recipe("creeper_banner_pattern").addInputs(["paper", "creeper_head"]).setOutput(
        "creeper_banner_pattern")

    config.shaped_recipe("crossbow").setEntries([(1, 0), (0, 2), (2, 2)], "stick").setEntries(
        [(0, 1), (2, 1)], "string").setEntry(1, 1, "tripwire_hook").setEntry(1, 2, "iron_ingot").setOutput("crossbow")

    config.shaped_recipe("cut_red_sandstone").setEntries(TWO_BY_TWO, "red_sandstone").setOutput(
        (4, "cut_red_sandstone"))
    generate_slab(config, "cut_red_sandstone_slab", "cut_red_sandstone")
    config.shaped_recipe("cut_sandstone").setEntries(TWO_BY_TWO, "sandstone").setOutput("cut_sandstone")
    generate_slab(config, "cut_sandstone_slab", "cut_sandstone")

    config.shapeless_recipe("cyan_dye").addInputs(["blue_dye", "green_dye"]).setOutput((2, "cyan_dye"))

    config.shaped_recipe("dark_prismarine").setEntries(AROUND_HOLLOW, "prismarine_shard").setEntry(
        1, 1, "black_dye").setOutput("dark_prismarine")
    generate_slab(config, "dark_prismarine_slab", "dark_prismarine")
    generate_stair(config, "dark_prismarine_stairs", "dark_prismarine")
    config.shaped_recipe("daylight_detector").setEntries(DOWNER_ROW, "#wooden_slabs").setEntries(
        [(0, 1), (1, 1), (2, 1)], "quartz").setEntries([(0, 2), (1, 2), (2, 2)], "glass").setOutput("daylight_detector")
    config.shaped_recipe("detector_rail").setEntries(
        [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)], "iron_ingot").setEntry(1, 0, "redstone").setEntry(
        1, 1, "stone_pressure_plate").setOutput("detector_rail")

    config.shapeless_recipe("diamond").addInput("diamond_block").setOutput((9, "diamond"))
    config.shaped_recipe("diamond_block").setEntries(THREE_BY_THREE, "diamond").setOutput("diamond_block")
    config.smelting_recipe("diamond_from_blasting", "minecraft:blasting").add_ingredient("diamond_ore").setOutput(
        "diamond").setXp(1).setCookingTime(100)
    config.smelting_recipe("diamond_from_blasting").add_ingredient("diamond_ore").setOutput("diamond").setXp(1)
    config.shaped_recipe("diorite").setEntries([(0, 0), (1, 1)], "quart").setEntries(
        [(1, 0), (0, 1)], "cobblestone").setOutput((2, "diorite"))
    generate_slab(config, "diorite_slab", "diorite")
    generate_stair(config, "diorite_stairs", "diorite")
    generate_wall(config, "diorite_wall", "diorite")
    config.shaped_recipe("dispenser").setEntries(leggings, "cobblestone").setEntry(1, 0, "redstone").setEntry(
        1, 1, "bow").setOutput("dispenser")
    config.shapeless_recipe("died_kelp").addInput("dried_kelp_block").setOutput((9, "dried_kelp"))
    config.shaped_recipe("dried_kelp_block").setEntries(THREE_BY_THREE, "dried_kelp").setOutput("dried_kelp_block")
    config.smelting_recipe("dried_kelp_from_smelting").add_ingredient("kelp").setOutput("dried_kelp").setXp(.1)
    config.smelting_recipe("dried_kelp_from_smelting", "campfire_cooking").add_ingredient("kelp").setOutput(
        "dried_kelp").setXp(.1).setCookingTime(600)
    config.smelting_recipe("dried_kelp_from_smelting", "minecraft:smoking").add_ingredient("kelp").setOutput("dried_kelp").setXp(
        .1).setCookingTime(100)
    config.shaped_recipe("dropper").setEntries(leggings, "cobblestone").setEntry(1, 0, "redstone").setOutput("dropper")
    config.shapeless_recipe("emerald").addInput("emerald_block").setOutput((9, "emerald"))
    config.shaped_recipe("emerald_block").setEntries(THREE_BY_THREE, "emerald").setOutput("emerald_block")
    config.smelting_recipe("emerald_from_smelting").add_ingredient("emerald_ore").setOutput("emerald").setXp(1)
    config.smelting_recipe("emerald_from_blasting").add_ingredient("emerald_ore").setOutput("emerald").setXp(
        1).setCookingTime(100)
    config.shaped_recipe("enchanting_table").setEntries(DOWNER_ROW + [(1, 1)], "obsidian").setEntries(
        [(0, 1), (2, 1)], "diamond").setEntry(1, 2, "book").setOutput("enchanting_table")
    config.shaped_recipe("end_crystal").setEntries(leggings, "glass").setEntry(1, 0, "ghast_tear").setEntry(
        1, 1, "ender_eye").setOutput("end_crystal")
    config.shaped_recipe("end_rod").setEntry(0, 0, "mineceraft:popped_chorus_fruit").setEntry(
        0, 1, "blaze_rod").setOutput((4, "end_rod"))
    generate_slab(config, "end_stone_brick_slab", "end_stone_bricks")
    generate_stair(config, "end_stone_brick_stairs", "end_stone_bricks")
    generate_wall(config, "end_stone_brick_wall", "end_stone_bricks")
    config.shaped_recipe("end_stone_bricks").setEntries(TWO_BY_TWO, "end_stone").setOutput((4, "end_stone_bricks"))
    config.shaped_recipe("ender_chest").setEntries(AROUND_HOLLOW, "obsidian").setEntry(1, 1, "ender_eye").setOutput(
        "ender_chest")
    config.shapeless_recipe("ender_eye").addInputs(["ender_pearl", "blaze_poweder"]).setOutput("ender_eye")
    config.shapeless_recipe("fermented_spider_eye").setOutput("fermented_spider_eye").addInputs(
        ["spider_eye", "brown_mushroom", "sugar"])
    config.shapeless_recipe("fire_charge").addInputs(
        ["gunpowder", "blaze_powder", ["coal", "charcoal"]]).setOutput((3, "fire_charge"))
    config.shaped_recipe("fishing_rod").setEntries([(0, 0), (1, 1), (2, 2)], "stick").setEntries(
        [(2, 0), (2, 1)], "string").setOutput("fishing_rod")
    config.shaped_recipe("fletching_table").setEntries(TWO_BY_TWO, "#planks").setEntries(
        [(0, 2), (1, 2)], "flint").setOutput("fletching_table")
    config.shapeless_recipe("flint_and_steel").addInputs(["iron_ingot", "flint"]).setOutput("flint_and_steel")
    config.shapeless_recipe("flower_banner_pattern").addInputs(["paper", "oseye_daisy"]).setOutput(
        "flower_banner_patter")
    config.shaped_recipe("flower_pot").setEntries(SMALL_V, "brick").setOutput("flower_pot")
    config.shaped_recipe("furnace").setEntries(AROUND_HOLLOW, "cobblestone").setOutput("furnace")
    config.shaped_recipe("furnace_minecart").setEntry(0, 0, "minecart").setEntry(
        0, 1, "furnace").setOutput("furnace_minecart")
    config.smelting_recipe("glass").add_ingredient("#sand").setOutput("glass").setXp(.1)
    config.shaped_recipe("glass_bottle").setEntries(SMALL_V, "glass").setOutput((3, "glass_bottle"))
    config.shaped_recipe("glass_pane").setEntries(THREE_BY_TWO, "glass").setOutput((16, "glass_pane"))
    config.shaped_recipe("glistering_melon_slice").setEntries(AROUND_HOLLOW, "gold_nugget").setEntry(
        1, 1, "melon_slice").setOutput("glistering_melon_slice")
    config.shaped_recipe("glowstone").setEntries(TWO_BY_TWO, "glowstone_dust").setOutput("glowstone")
    config.shaped_recipe("gold_block").setEntries(THREE_BY_THREE, "gold_block").setOutput("gold_block")
    config.smelting_recipe("gold_ingot").add_ingredient("gold_ore").setOutput("gold_ingot").setXp(1.)
    config.smelting_recipe("gold_ingot_from_blasting").add_ingredient("gold_ore").setOutput("gold_ingot").setXp(
        1.).setCookingTime(100)
    config.shapeless_recipe("gold_ingot_from_gold_block").addInput("gold_block").setOutput((9, "gold_ingot"))
    config.shaped_recipe("gold_ingot_from_nuggets").setEntries(THREE_BY_THREE, "gold_nugget").setOutput("gold_ingot")
    config.shapeless_recipe("gold_nugget").addInput("gold_ingot").setOutput((9, "gold_nugget"))
    GOLDEN_RECOVER = ["golden_pickaxe", "golden_shovel", "golden_axe", "golden_hoe", "golden_sword", "golden_helmet",
                      "golden_chestplate", "golden_leggings", "golden_boots", "golden_horse_armor"]
    config.smelting_recipe("gold_nugger_from_blasting", "minecraft:blasting").add_ingredient(GOLDEN_RECOVER).setOutput(
        "golden_nugget").setXp(.1).setCookingTime(100)
    config.smelting_recipe("gold_nugger_from_blasting").add_ingredient(GOLDEN_RECOVER).setOutput("golden_nugget").setXp(
        .1)
    config.shaped_recipe("golden_apple").setEntries(AROUND_HOLLOW, "gold_ingot").setEntry(1, 1, "apple").setOutput(
        "golden_apple")
    config.shaped_recipe("golden_carrot").setEntries(AROUND_HOLLOW, "gold_nugget").setEntry(1, 1, "carrot").setOutput(
        "golden_carrot")
    config.shapeless_recipe("granite").addInputs(["granite", "quartz"]).setOutput("granite")
    generate_slab(config, "granite_slab", "granite")
    generate_stair(config, "granite_stairs", "granite")
    generate_wall(config, "granite_wall", "granite")
    config.shapeless_recipe("gray_dye").addInputs(["black_dye", "white_dye"]).setOutput((2, "gray_dye"))
    config.smelting_recipe("green_dye").add_ingredient("cactus").setOutput("green_dye").setXp(1.)
    config.shaped_recipe("grindstone").setEntries([(0, 0), (2, 0)], "#planks").setEntries(
        [(0, 1), (2, 1)], "stick").setEntry(1, 1, "stone_slab").setOutput("grindstone")
    config.shaped_recipe("hay_block").setEntries(THREE_BY_THREE, "wheat").setOutput("hay_block")
    config.shaped_recipe("heavy_weighted_pressure_plate").setEntries([(0, 0), (1, 0)], "iron_ingot").setOutput(
        "heavy_weighted_pressure_plate")
    config.shaped_recipe("honey_block").setEntries(TWO_BY_TWO, "honey_bottle").setOutput("honey_block")
    config.shapeless_recipe("honey_bottle").addInput("honey_block").addInput("glass_bottle", 4).setOutput(
        (4, "honey_bottle"))
    config.shaped_recipe("honeycomb_block").setEntries(TWO_BY_TWO, "honeycomb").setOutput("honeycomb_block")
    config.shaped_recipe("hopper").setEntries(
        [(0, 1), (0, 2), (1, 0), (2, 1), (2, 2)], "iron_ingot").setEntry(1, 1, "chest").setOutput("hopper")
    config.shaped_recipe("hopper_minecart").setEntry(0, 0, "minecart").setEntry(0, 1, "hopper").setOutput(
        "hopper_minecart")
    config.shaped_recipe("iron_bars").setEntries(THREE_BY_TWO, "iron_ingot").setOutput("iron_bars")
    config.shaped_recipe("iron_block").setEntries(THREE_BY_THREE, "iron_ingot").setOutput("iron_block")
    config.shaped_recipe("iron_door").setEntries(TWO_BY_THREE, "iron_ingot").setOutput("iron_door")
    config.smelting_recipe("iron_ingot").add_ingredient("iron_ore").setOutput("iron_ingot").setXp(.7)
    config.smelting_recipe("iron_ingot", "minecraft:blasting").add_ingredient("iron_ore").setOutput("iron_ingot").setXp(
        .7).setCookingTime(100)
    config.shapeless_recipe("iron_ingot_from_iron_block").addInput("iron_block").setOutput((9, "iron_ingot"))
    config.shaped_recipe("iron_ingot_from_nuggets").setEntries(THREE_BY_THREE, "iron_nugget").setOutput("iron_ingot")
    config.shapeless_recipe("iron_nugget").addInput("iron_ingot").setOutput((9, "iron_nugget"))
    IRON_RECOVER = ["iron_pickaxe", "iron_shovel", "iron_axe", "iron_hoe", "iron_sword", "iron_helmet",
                    "iron_chestplate", "iron_leggings", "iron_boots", "iron_horse_armor", "chainmail_helmet",
                    "chainmail_chestplate", "chainmail_leggings", "chainmail_boots"]
    config.smelting_recipe("iron_nugget_from_blasting", "minecraft:blasting").add_ingredient(IRON_RECOVER).setOutput(
        "iron_nugget").setXp(.1).setCookingTime(100)
    config.smelting_recipe("iron_nugget_from_smelting").add_ingredient(IRON_RECOVER).setOutput("iron_nugget").setXp(.1)
    config.shaped_recipe("iron_trapdoor").setEntries(TWO_BY_TWO, "iron_ingot").setOutput("iron_trapdoor")
    config.shaped_recipe("item_frame").setEntries(AROUND_HOLLOW, "stick").setEntry(1, 1, "leather").setOutput(
        "item_frame")
    config.shaped_recipe("jack_o_lantern").setEntry(0, 0, "torch").setEntry(0, 1, "carved_pumpkin").setOutput(
        "jack_o_lantern")
    config.shaped_recipe("jukebox").setEntries(AROUND_HOLLOW, "#planks").setEntry(1, 1, "diamond").setOutput("jukebox")
    config.shaped_recipe("ladder").setEntries([(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2), (1, 1)],
                                              "stick").setOutput((3, "ladder"))
    config.shaped_recipe("lantern").setEntries(AROUND_HOLLOW, "iron_nugget").setEntry(
        1, 1, "torch").setOutput("lantern")
    config.shaped_recipe("lapis_block").setEntries(THREE_BY_THREE, "lapis_lazuli").setOutput("lapis_block")


