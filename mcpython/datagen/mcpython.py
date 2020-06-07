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


DEFAULT_OUTPUT = G.local+"/resources/generated"


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
        (4, "minecraft:{}".format(w))).setGroup("planks")
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
def generate_data():
    if "--data-gen" not in sys.argv: return  # data gen only when launched so, not when we think
    if os.path.exists(DEFAULT_OUTPUT):
        shutil.rmtree(DEFAULT_OUTPUT)
    os.makedirs(DEFAULT_OUTPUT)
    config = Configuration.DataGeneratorConfig("minecraft", G.local+"/resources/generated")

    for w in ["acacia", "birch", "oak", "jungle", "spruce", "dark_oak"]:
        generate_wooded_recipes(config, w)

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

