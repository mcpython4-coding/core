"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft

This project is not official by mojang and does not relate to it.
"""
from mcpython import globals as G
from mcpython.common.data.datagen.Configuration import DataGeneratorConfig
from mcpython.common.data.datagen.BlockModelGenerator import BlockStateGenerator, ModelRepresentation, MultiPartBlockStateGenerator
import sys
from mcpython.util.enums import EnumSide

DEFAULT_OUTPUT = G.local + "/resources/generated"  # where to output data - in dev environment


def generate_button_template(config):
    model = "alias:"
    state = BlockStateGenerator(config, "button_template")
    for power in (True, False):
        state.add_state("face=ceiling,facing=east,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=270, r_x=180))
        state.add_state("face=ceiling,facing=north,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=180, r_x=180))
        state.add_state("face=ceiling,facing=south,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_x=180))
        state.add_state("face=ceiling,facing=west,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=90, r_x=180))

        state.add_state("face=floor,facing=east,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=90))
        state.add_state("face=floor,facing=north,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal")))
        state.add_state("face=floor,facing=south,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=180))
        state.add_state("face=floor,facing=west,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=270))

        state.add_state("face=wall,facing=east,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=90, r_x=90, uvlock=True))
        state.add_state("face=wall,facing=north,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_x=90, uvlock=True))
        state.add_state("face=wall,facing=south,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=180, r_x=90, uvlock=True))
        state.add_state("face=wall,facing=west,powered={}".format(str(power).lower()),
                        ModelRepresentation(model + ("pressed" if power else "normal"), r_y=270, r_x=90, uvlock=True))


def generate_button_state(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    BlockStateGenerator(config, name).addAliasName("alias:pressed", model + "_pressed").addAliasName("alias:normal", model)


def generate_door_template(config):
    model = "alias:"
    state = BlockStateGenerator(config, "door_template")
    for side in (0, 1):
        model = model + ("bottom" if side == 0 else "top")
        half = "lower" if side == 0 else "upper"
        state.add_state("facing=east,half={},hinge=left,open=false".format(half), model + "_default")
        state.add_state("facing=east,half={},hinge=left,open=true".format(half), ModelRepresentation(model + "_hinge", r_y=90))
        state.add_state("facing=east,half={},hinge=right,open=false".format(half), model + "_hinge")
        state.add_state("facing=east,half={},hinge=right,open=true".format(half), ModelRepresentation(model + "_default", r_y=270))

        state.add_state("facing=north,half={},hinge=left,open=false".format(half), ModelRepresentation(model + "_default", r_y=270))
        state.add_state("facing=north,half={},hinge=left,open=true".format(half), model + "_hinge")
        state.add_state("facing=north,half={},hinge=right,open=false".format(half), ModelRepresentation(model + "_hinge", r_y=270))
        state.add_state("facing=north,half={},hinge=right,open=true".format(half), ModelRepresentation(model + "_default", r_y=180))

        state.add_state("facing=south,half={},hinge=left,open=false".format(half), ModelRepresentation(model + "_default", r_y=90))
        state.add_state("facing=south,half={},hinge=left,open=true".format(half), ModelRepresentation(model + "_hinge", r_y=180))
        state.add_state("facing=south,half={},hinge=right,open=false".format(half), ModelRepresentation(model + "_hinge", r_y=90))
        state.add_state("facing=south,half={},hinge=right,open=true".format(half), model + "_default")

        state.add_state("facing=west,half={},hinge=left,open=false".format(half), ModelRepresentation(model + "_default", r_y=180))
        state.add_state("facing=west,half={},hinge=left,open=true".format(half), ModelRepresentation(model + "_hinge", r_y=270))
        state.add_state("facing=west,half={},hinge=right,open=false".format(half), ModelRepresentation(model + "_hinge", r_y=180))
        state.add_state("facing=west,half={},hinge=right,open=true".format(half), ModelRepresentation(model + "_default", r_y=90))


def generate_door_state(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    BlockStateGenerator(config, name, parent="minecraft:door_template").addAliasName("alias:bottom_default", model + "_bottom").addAliasName(
        "top_default", model + "_top").addAliasName("alias:bottom_hinge", model + "_bottom_hinge").addAliasName("alias:top_hinge", model + "_top_hinge")


def generate_trapdoor_template(config):
    model = "alias:"
    state = BlockStateGenerator(config, "trapdoor_template")
    for delta, face in [(90, "east"), (0, "north"), (180, "south"), (270, "west")]:
        state.add_state("facing={},half=bottom,open=false".format(face), ModelRepresentation(model + "bottom", r_y=delta))
        state.add_state("facing={},half=bottom,open=true".format(face), ModelRepresentation(model + "open", r_y=delta))
        state.add_state("facing={},half=top,open=false".format(face), ModelRepresentation(model + "top", r_y=delta))
        state.add_state("facing={},half=top,open=true".format(face), ModelRepresentation(model + "open", r_x=180, r_y=180 + delta))


def generate_trapdoor(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    BlockStateGenerator(config, name, parent="minecraft:trapdoor_template").addAliasName("alias:bottom", model + "_bottom").addAliasName(
        "alias:open", model + "_open").addAliasName("alias:top", model + "_top")


def generate_fence_template(config):
    model = "alias:"
    state = MultiPartBlockStateGenerator(config, "fence_template")
    state.add_state(None, model + "post")
    state.add_state("north=true", ModelRepresentation(model + "side", uvlock=True))
    state.add_state("east=true", ModelRepresentation(model + "side", uvlock=True, r_y=90))
    state.add_state("south=true", ModelRepresentation(model + "side", uvlock=True, r_y=180))
    state.add_state("west=true", ModelRepresentation(model + "side", uvlock=True, r_y=270))


def generate_fence_state(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    MultiPartBlockStateGenerator(config, name, parent="minecraft:fence_template", optimize=False).addAliasName("alias:post", model + "_post").addAliasName(
        "alias:side", model + "_side")


def generate_fence_gate_template(config):
    model = "alias:"
    state = BlockStateGenerator(config, "fence_gate_template", generate_alias=0)
    for o in (0, 1):
        for w in (0, 1):
            m = model + ("default" if w == 0 else "wall") + ("" if o == 0 else "_open")
            op = str(bool(o)).lower()
            wp = str(bool(w)).lower()
            state.add_state("facing=east,in_wall={},open={}".format(wp, op), ModelRepresentation(m, r_y=270, uvlock=True))
            state.add_state("facing=north,in_wall={},open={}".format(wp, op), ModelRepresentation(m, r_y=180, uvlock=True))
            state.add_state("facing=south,in_wall={},open={}".format(wp, op), ModelRepresentation(m, uvlock=True))
            state.add_state("facing=west,in_wall={},open={}".format(wp, op), ModelRepresentation(m, uvlock=True, r_y=90))


def generate_fence_gate_state(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    BlockStateGenerator(config, name, parent="minecraft:fence_gate_template").addAliasName("alias:default", model).addAliasName(
        "alias:default_open", model + "_open").addAliasName("alias:wall", model + "_wall").addAliasName("alias_wall_open", model + "_wall_open")


def generate_pressure_plate_state(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    state = BlockStateGenerator(config, name)
    state.add_state("powered=false", model)
    state.add_state("powered=true", model + "_down")


def generate_stair_base(config):
    model = "alias:"
    state = BlockStateGenerator(config, "stair_template", generate_alias=0)
    for facing, delta in [(EnumSide.EAST, 0), (EnumSide.NORTH, -90), (EnumSide.SOUTH, -270), (EnumSide.WEST, -180)]:
        name = facing.normal_name
        state.add_state("facing={},half=bottom,shape=inner_left".format(name), ModelRepresentation(model + "inner", r_y=270 + delta, uvlock=True))
        state.add_state("facing={},half=bottom,shape=inner_right".format(name), ModelRepresentation(model + "inner", r_y=delta, uvlock=True))
        state.add_state("facing={},half=bottom,shape=outer_left".format(name), ModelRepresentation(model + "outer", r_y=270 + delta, uvlock=True))
        state.add_state("facing={},half=bottom,shape=outer_right".format(name), ModelRepresentation(model + "outer", r_y=delta, uvlock=True))
        state.add_state("facing={},half=bottom,shape=straight".format(name), ModelRepresentation(model + "default", r_y=delta, uvlock=True))
        state.add_state("facing={},half=top,shape=inner_left".format(name), ModelRepresentation(model + "inner", r_x=180, r_y=delta, uvlock=True))
        state.add_state("facing={},half=top,shape=inner_right".format(name), ModelRepresentation(model + "inner", r_x=180, r_y=90 + delta, uvlock=True))
        state.add_state("facing={},half=top,shape=outer_left".format(name), ModelRepresentation(model + "outer", r_x=180, r_y=delta, uvlock=True))
        state.add_state("facing={},half=top,shape=outer_right".format(name), ModelRepresentation(model + "outer", r_x=180, r_y=90 + delta, uvlock=True))
        state.add_state("facing={},half=top,shape=straight".format(name), ModelRepresentation(model + "default", r_x=180, r_y=delta))


def generate_stairs_state(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    BlockStateGenerator(config, name, parent="minecraft:stair_template").addAliasName("alias:inner", model + "_inner").addAliasName("alias:outer", model + "_outer").addAliasName(
        "alias:default", model)


def generate_one_to_one(config, name):
    model = "{}:block/{}".format(config.default_namespace, name)
    BlockStateGenerator(config, name).add_state(None, model)


def generate_wall_template(config):
    MultiPartBlockStateGenerator(config, "wall_template").add_state("up=true", "alias:post").add_state(
        "north=low", "alias:side").add_state("east=low", ModelRepresentation("alias:side", r_y=90)).add_state(
        "south=low", ModelRepresentation("alias:side", r_y=180)).add_state("west=low", ModelRepresentation(
        "alias:side", r_y=270)).add_state("north=tall", "alias:tall").add_state(
        "east=tall", ModelRepresentation("alias:tall", r_y=90)).add_state("south=tall", ModelRepresentation(
        "alias:tall", r_y=180)).add_state("west=tall", ModelRepresentation("alias:tall", r_y=270))


def generate_log_template(config):
    BlockStateGenerator(config, "log_template").add_state("axis=x", ModelRepresentation("alias:horizontal", r_x=90, r_y=90)).add_state(
        "axis=y", "alias:normal").add_state("axis=z", ModelRepresentation("alias:horizontal", r_x=90))


@G.modloader("minecraft", "special:datagen:configure")
def generate_recipes():
    """
    generator for all non-combined-generated block models in minecraft
    """

    if "--data-gen" not in sys.argv: return  # data gen only when launched so, not when we think
    config = DataGeneratorConfig("minecraft", G.local + "/resources/generated")
    config.setDefaultNamespace("minecraft")

    generate_wall_template(config)
    generate_log_template(config)

    generate_fence_template(config)
    generate_fence_gate_template(config)
    generate_trapdoor_template(config)
    generate_door_template(config)
    generate_button_template(config)
    for wood in ["acacia", "birch", "jungle", "oak", "dark_oak", "crimson", "warped"]:
        generate_button_state(config, "{}_button".format(wood))
        generate_door_state(config, "{}_door".format(wood))
        generate_trapdoor(config, "{}_trapdoor".format(wood))
        generate_fence_state(config, "{}_fence".format(wood))
        generate_fence_gate_state(config, "{}_fence_gate".format(wood))
        generate_pressure_plate_state(config, "{}_pressure_plate".format(wood))
        if wood not in ("crimson", "warped"):
            generate_one_to_one(config, "{}_sapling".format(wood))
        generate_one_to_one(config, "{}_sign".format(wood))
        generate_one_to_one(config, "{}_wall_sign".format(wood))
        generate_stairs_state(config, "{}_stairs".format(wood))

    generate_button_state(config, "stone_button")
    generate_button_state(config, "polished_blackstone_button")
    generate_door_state(config, "iron_door")
    generate_trapdoor(config, "iron_trapdoor")
    generate_fence_state(config, "nether_fence")
    generate_pressure_plate_state(config, "stone_pressure_plate")
    generate_pressure_plate_state(config, "polished_blackstone_pressure_plate")

    generate_stair_base(config)
    for e in [
        "stone_brick", "stone", "smooth_quartz", "smooth_red_sandstone",
        "smooth_sandstone", "sandstone", "red_sandstone", "quartz", "red_nether_brick",
        "prismarine_brick", "prismarine", "purpur", "polished_granite", "polished_andesite",
        "polished_blackstone_brick", "polished_blackstone" "polished_diorite",
        "nether_brick", "mossy_cobblestone", "mossy_stone_brick", "granite", "end_stone_brick",
        "diorite", "dark_prismarine", "cobblestone", "brick", "blackstone", "andesite"
    ]:
        generate_stairs_state(config, "{}_stairs".format(e))

    generate_one_to_one(config, "allium")
    generate_one_to_one(config, "azure_bluet")
    generate_one_to_one(config, "blue_orchid")
    generate_one_to_one(config, "brown_mushroom")
    generate_one_to_one(config, "cornflower")
    generate_one_to_one(config, "crimson_fungus")
    generate_one_to_one(config, "crimson_roots")
    generate_one_to_one(config, "dandelion")
    generate_one_to_one(config, "dead_bush")
    generate_one_to_one(config, "fern")

    generate_one_to_one(config, "bamboo_sapling")
    generate_one_to_one(config, "cactus")
    generate_one_to_one(config, "cobweb")
    generate_one_to_one(config, "ancient_debris")
    generate_one_to_one(config, "barrier")
    generate_one_to_one(config, "beacon")
    for color in ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray",
                  "cyan", "blue", "purple", "green", "brown", "red", "black"]:
        generate_one_to_one(config, "{}_banner".format(color))
        generate_one_to_one(config, "{}_wall_banner".format(color))
        generate_one_to_one(config, "{}_carpet".format(color))
        generate_one_to_one(config, "{}_shulker_box".format(color))
        generate_one_to_one(config, "{}_bed".format(color))
    generate_one_to_one(config, "shulker_box")
    generate_one_to_one(config, "blue_ice")

    for c in ["brain", "tube", "horn", "bubble"]:
        generate_one_to_one(config, "{}_coral".format(c))
        generate_one_to_one(config, "{}_coral_block".format(c))
        generate_one_to_one(config, "{}_coral_fan".format(c))
        generate_one_to_one(config, "dead_{}_coral".format(c))
        generate_one_to_one(config, "dead_{}_coral_block".format(c))
        generate_one_to_one(config, "dead_{}_coral_fan".format(c))

    generate_one_to_one(config, "bubble_column")
    generate_one_to_one(config, "chain")
    generate_one_to_one(config, "chiseled_quartz_block")
    generate_one_to_one(config, "chiseled_sandstone")
    generate_one_to_one(config, "chiseled_red_sandstone")
    generate_one_to_one(config, "cut_sandstone")
    generate_one_to_one(config, "cut_red_sandstone")
    generate_one_to_one(config, "crimson_nylium")
    generate_one_to_one(config, "dried_kelp_block")
    generate_one_to_one(config, "enchanting_table")
    generate_one_to_one(config, "end_gateway")
    generate_one_to_one(config, "end_portal")

    generate_one_to_one(config, "cartography_table")
    generate_one_to_one(config, "crafting_table")
