"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
from mcpython import globals as G
from mcpython.datagen import Configuration, EntityModelGenerator
import shutil
import os
import sys

DEFAULT_OUTPUT = G.local + "/resources/generated"  # where to output data - in dev environment


@G.modloader("minecraft", "special:datagen:configure")
def generate_recipes():
    """
    generator for all entity data stuff in minecraft
    Values from minecraft forge's decompiled mc code, for mc version 1.16.1
    """

    if "--data-gen" not in sys.argv: return  # data gen only when launched so, not when we think
    config = Configuration.DataGeneratorConfig("minecraft", G.local + "/resources/generated")
    config.setDefaultNamespace("minecraft")

    """
    armor_stand_generator = EntityModelGenerator.EntityModelGenerator(config, "armor_stand")# .setInvertedY(True)
    texture = "assets/minecraft/textures/entity/armorstand/wood.png"
    tex_size = 64, 64
    armor_stand_generator.addBox("head",             texture, tex_size, (-1, -7, -1),  (2, 7, 2),   (0, 0))
    armor_stand_generator.addBox("body",             texture, tex_size, (-6, 0, -1.5), (12, 3, 3),  (0, 26))
    armor_stand_generator.addBox("right_arm",        texture, tex_size, (-2, -2, -1),  (2, 12, 2),  (24, 0),  rotation_center=(-5, 2, 0))
    armor_stand_generator.addBox("left_arm",         texture, tex_size, (0, -2, -1),   (2, 12, 2),  (32, 16), rotation_center=(5, 2, 0))  # mirror=true
    armor_stand_generator.addBox("right_leg",        texture, tex_size, (-1, 0, -1),   (2, 11, 2),  (8, 0),   rotation_center=(-1.9, 12, 0))
    armor_stand_generator.addBox("left_leg",         texture, tex_size, (-1, 0, -1),   (2, 11, 2),  (48, 16), rotation_center=(1.9, 12, 0))  # mirror=true
    armor_stand_generator.addBox("right_side_stand", texture, tex_size, (-3, 3, -1),   (2, 7, 2),   (16, 0))  # showModel = true
    armor_stand_generator.addBox("left_side_stand",  texture, tex_size, (1, 3, -1),    (2, 7, 2),   (48, 16))
    armor_stand_generator.addBox("waist_stand",      texture, tex_size, (-4, 10, -1),  (8, 2, 2),   (0, 48))
    armor_stand_generator.addBox("base_stand",       texture, tex_size, (-6, 11, -6),  (12, 1, 12), (0, 32),  rotation_center=(0, 12, 0))

    armor_stand_generator.add_state("default", "head", "body", "right_arm", "left_arm", "right_leg", "left_leg", "right_side_stand", "left_side_stand",
                                    "waist_stand", "base_stand")"""
