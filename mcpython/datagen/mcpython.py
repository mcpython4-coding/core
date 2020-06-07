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


DEFAULT_OUTPUT = G.local+"/resources/generated"  # where to output data - in dev environment

if not G.dev_environment:
    DEFAULT_OUTPUT = G.local  # when we are not in dev-environment, store them when needed in G.local


def generate_slab(config, name, base):
    config.shaped_recipe(name).setGroup("slab").setEntries([(0, 0), (1, 0), (2, 0)], "minecraft:"+base).setOutput(
        (6, "minecraft:"+name))


def generate_stair(config, name, base):
    config.shaped_recipe(name).setGroup("stair").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)], "minecraft:"+base).setOutput(
        (4, "minecraft:"+name))


def generate_wall(config, name, base):
    config.shaped_recipe(name).setGroup("wall").setEntries(
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)], "minecraft:"+base).setOutput((6, "minecraft:"+name))


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
        [(0, 0), (1, 0), (2, 0)], "minecraft:{}_planks".format(w)).setOutput((6, "minecraft:{}_slab".format(w)))
    config.shaped_recipe("{}_stairs".format(w)).setGroup("wooded_stairs").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)], "minecraft:{}_planks".format(w)).setOutput(
        (4, "minecraft:{}_stairs".format(w)))
    config.shaped_recipe("{}_trapdoor".format(w)).setGroup("wooden_trapdoor").setEntries(
        [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)], "minecraft:{}_planks".format(w)).setOutput(
        (2, "minecraft:{}_trapdoor".format(w)))
    config.shaped_recipe("{}_wood".format(w)).setGroup("bark").setEntries(
        [(0, 0), (1, 0), (0, 1), (1, 1)], "minecraft:{}_log".format(w)).setOutput((3, "minecraft:{}_wood".format(w)))


@G.modloader("minecraft", "special:datagen:configure")
def generate_recipes():
    """
    generator for all recipes in minecraft
    """

    if "--data-gen" not in sys.argv: return  # data gen only when launched so, not when we think
    if os.path.exists(DEFAULT_OUTPUT):
        shutil.rmtree(DEFAULT_OUTPUT)
    os.makedirs(DEFAULT_OUTPUT)
    config = Configuration.DataGeneratorConfig("minecraft", G.local+"/resources/generated")

    for w in ["acacia", "birch", "oak", "jungle", "spruce", "dark_oak"]:
        generate_wooded_recipes(config, w)

    for c in ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray",
              "cyan", "blue", "purple", "green", "brown", "red", "black"]:
        config.shaped_recipe("{}_banner".format(c)).setGroup("banner").setEntries(
            [(0, 1), (0, 2), (1, 1), (1, 2), (2, 1), (2, 2)], "minecraft:{}_wool".format(c)).setEntry(
            1, 0, "minecraft:stick").setOutput("minecraft:{}_banner".format(c))
        config.shaped_recipe("{}_bed".format(c)).setGroup("bed").setEntries(
            [(0, 0), (1, 0), (2, 0)], "#minecraft:planks").setEntries(
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
    config.shaped_recipe("beacon").setEntries([(0, 0), (1, 0), (2, 0)], "minecraft:obsidian").setEntries(
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
    config.shaped_recipe("blast_furnace").setEntries([(0, 0), (1, 0), (2, 0)], "minecraft:smooth_stone").setEntries(
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

