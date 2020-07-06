"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.15.2.jar of minecraft, downloaded on 1th of February, 2020"""
import globals as G
import mcpython.datagen.BlockModelGenerator
import mcpython.datagen.Configuration
import mcpython.factory.BlockFactory
import enum
import typing
from mcpython.datagen.BlockModelGenerator import ModelRepresentation
import mcpython.block.BlockWall
from mcpython.datagen.RecipeGenerator import ShapedRecipeGenerator


WALL_TEMPLATE = sum([[(x, y) for y in range(2)] for x in range(3)], [])
SLAB_TEMPLATE = [(x, 0) for x in range(3)]


def generate_full_block_slab_wall(config: mcpython.datagen.Configuration.DataGeneratorConfig, name: str,
                                  texture: str = None, enable=(True, True, True), callback=None,
                                  slab_name=None, wall_name=None, generate_recipes=(True, True), textures=None):
    assert textures is None or (type(textures) in (list, set, tuple) and len(textures) <= 3), \
        "textures must be either None or iterable of length 3 or less"
    if texture is None: texture = "{}:block/{}".format(*name.split(":"))
    if slab_name is None: slab_name = name + "_slab"
    if wall_name is None: wall_name = name + "_wall"
    if type(enable) == dict:
        enable = (True if name not in enable else enable[name], True if slab_name not in enable else enable[slab_name],
                  True if wall_name not in enable else enable[wall_name])
    if enable[0] if type(enable[0]) == bool else enable[0][name]:
        generate_full_block(config, name, texture if textures is None else textures[0], callback)
    if enable[1] if type(enable[1]) == bool else enable[1][slab_name]:
        generate_slab_block(config, slab_name, texture if textures is None else textures[1], callback,
                            generate_recipes[0])
    if enable[2] if type(enable[2]) == bool else enable[2][wall_name]:
        generate_wall_block(config, wall_name, texture if textures is None else textures[2], callback,
                            generate_recipes[1])


def generate_full_block(config, name: str, texture: str = None, callback=None):
    if texture is None: texture = "{}:block/{}".format(*name.split(":"))
    modname, raw_name = name.split(":")
    CombinedFullBlockFactory(modname, config, on_create_callback=callback).setName(name).setTextureVariable(
        "all", texture)


def generate_slab_block(config, name: str, texture: str = None, callback=None, generate_recipe=True):
    if texture is None: texture = "{}:block/{}".format(*name.split("_slab")[0].split(":"))
    modname, raw_name = name.split(":") if name.count(":") == 1 else (config.modname, name)
    CombinedSlabFactory(texture, modname, config, full_model="{}:block/{}".format(modname, raw_name),
                        on_create_callback=callback).setName(name)
    if generate_recipe:
        mcpython.datagen.RecipeGenerator.ShapedRecipeGenerator(name, config).setEntries(
            SLAB_TEMPLATE, name.split("_slab")[0]).setOutput((6, name)).setGroup("slab")


def generate_wall_block(config, name: str, texture: str = None, callback=None, generate_recipe=True):
    if texture is None: texture = "{}:block/{}".format(*name.split("_wall")[0].split(":"))
    modname, raw_name = name.split(":")
    CombinedWallFactory(texture, modname, config, on_create_callback=callback).setName(name)
    if generate_recipe:
        mcpython.datagen.RecipeGenerator.ShapedRecipeGenerator(name, config).setEntries(
            WALL_TEMPLATE, name.split("_wall")[0]).setOutput((6, name)).setGroup("wall")


def generate_log_block(config, name: str, front_texture: str = None, side_texture: str = None, callback=None):
    if front_texture is None: front_texture = "{}:block/{}_top".format(*name.split(":"))
    if side_texture is None: side_texture = "{}:block/{}".format(*name.split(":"))
    modname, raw_name = name.split(":")
    CombinedLogFactory(front_texture, side_texture, modname, config, on_create_callback=callback).setName(name)


class CombinedFullBlockFactoryMode(enum.Enum):
    """
    enum representing different "kinds" of cubes for the CombinedFullBlockFactory
    """

    CUBE = ("minecraft:block/cube", {"up", "down", "north", "south", "east", "west"})
    CUBE_ALL = ("minecraft:block/cube_all", {"all"})
    BOTTOM_TOP = ("minecraft:block/cube_bottom_top", {"bottom", "top", "side"})
    COLUMN = ("minecraft:block/cube_column", {"end", "side"})
    COLUMN_HORIZONTAL = ("minecraft:block/cube_column_horizontal", {"end", "side"})
    DIRECTIONAL = ("minecraft:block/cube_directional", {"up", "down", "north", "south", "east", "west"})
    TOP = ("minecraft:block/cube_top", {"top", "side"})

    def __init__(self, parent_name: str, texture_names: set):
        self.parent = parent_name
        self.texture_names = texture_names


class CombinedFullBlockFactory:
    """
    Factory for creating any kind of blocks with only one model (like any full blocks).
    This does NOT include slabs as they are based on two models
    """

    GLOBAL_NAME = None

    def __init__(self, modname=None, config=None, on_create_callback=None):
        if modname is None: modname = self.GLOBAL_NAME
        assert modname is not None, "modname must be set locally or globally"
        if config is None: config = mcpython.datagen.Configuration.DataGeneratorConfig(modname,
                                                                                       G.modloader.mods[modname].path)
        self.config = config
        self.mode = CombinedFullBlockFactoryMode.CUBE_ALL
        self.textures = {}
        self.modname = modname
        self.name = None
        self.on_create_callback = on_create_callback
        G.modloader(modname, "stage:combined_factory:build")(self.build)

    def setName(self, name: str):
        self.name = name
        return self

    def setMode(self, mode: CombinedFullBlockFactoryMode):
        self.mode = mode
        return self

    def setTextureVariable(self, name: str, location: str):
        self.textures[name] = location

    def build(self):
        assert all([name in self.textures for name in self.mode.texture_names]), "all needed texture names MUST be set"
        assert self.name is not None, "name must be set"
        G.modloader(self.modname, "special:datagen:configure")(self.__generate_data_gen)
        G.modloader(self.modname, "stage:block:factory_usage")(self.__generate_factories)

    def __generate_data_gen(self):
        name = ":".join(self.name.split(":")[1:])
        model_gen = mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name, parent=self.mode.parent)
        [model_gen.set_texture_variable(name, self.textures[name]) for name in self.textures]
        mcpython.datagen.BlockModelGenerator.BlockStateGenerator(
            self.config, name).add_state(None, "{}:block/{}".format(self.modname, name))

    def __generate_factories(self):
        factory = mcpython.factory.BlockFactory.BlockFactory().setName(self.name)
        if self.on_create_callback is not None: self.on_create_callback(self, factory)
        factory.finish()


class CombinedSlabFactory:
    """
    CombinedFactory for slabs
    """

    GLOBAL_NAME = None
    SLAB_TEXTURES = {"top", "bottom", "side"}

    def __init__(self, texture: str, modname=None, config=None, on_create_callback=None, full_model=None):
        """
        will create an n ew CombinedSlabFactory
        :param texture: the texture for the slab
        :param modname: the modname, if not set globally
        :param config: the config to use
        :param on_create_callback: callback when BlockFactory is active
        :param full_model: the model for the full block, if existent
        """
        if modname is None: modname = self.GLOBAL_NAME
        assert modname is not None, "modname must be set locally or globally"
        if config is None: config = mcpython.datagen.Configuration.DataGeneratorConfig(modname,
                                                                                       G.modloader.mods[modname].path)
        self.config = config
        self.texture = texture
        self.modname = modname
        self.name = None
        self.on_create_callback = on_create_callback
        self.full_model = full_model
        G.modloader(modname, "stage:combined_factory:build")(self.build)

    def setName(self, name: str):
        self.name = name
        return self

    def build(self):
        assert self.name is not None, "name must be set"
        G.modloader(self.modname, "special:datagen:configure")(self.__generate_data_gen)
        G.modloader(self.modname, "stage:block:factory_usage")(self.__generate_factories)

    def __generate_data_gen(self):
        name = ":".join(self.name.split(":")[1:])
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name, parent="minecraft:block/slab").set_texture_variables(self.texture, *self.SLAB_TEXTURES)
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name + "_top", parent="minecraft:block/slab_top"
        ).set_texture_variables(self.texture, *self.SLAB_TEXTURES)
        if not self.full_model:
            self.full_model = "{}:block/{}_double".format(self.modname, self.name)
            mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
                self.config, name + "_double", parent="minecraft:block/cube_all").set_texture_variable(
                "all", self.texture)
        mcpython.datagen.BlockModelGenerator.BlockStateGenerator(
            self.config, name).add_state("type=bottom", "{}:block/{}".format(self.modname, name)).add_state(
            "type=top", "{}:block/{}".format(self.modname, name)).add_state("type=double", self.full_model)

    def __generate_factories(self):
        factory = mcpython.factory.BlockFactory.BlockFactory().setName(self.name).setSlab()
        if self.on_create_callback is not None: self.on_create_callback(self, factory)
        factory.finish()


class CombinedWallFactory:
    """
    CombinedFactory for walls
    """

    GLOBAL_NAME = None

    def __init__(self, texture: str, modname=None, config=None, on_create_callback=None):
        """
        will create an n ew CombinedWallFactory
        :param texture: the texture for the slab
        :param modname: the modname, if not set globally
        :param config: the config to use
        :param on_create_callback: callback when BlockFactory is active
        """
        if modname is None: modname = self.GLOBAL_NAME
        assert modname is not None, "modname must be set locally or globally"
        if config is None: config = mcpython.datagen.Configuration.DataGeneratorConfig(modname,
                                                                                       G.modloader.mods[modname].path)
        self.config = config
        self.texture = texture
        self.modname = modname
        self.name = None
        self.on_create_callback = on_create_callback
        G.modloader(modname, "stage:combined_factory:build")(self.build)

    def setName(self, name: str):
        self.name = name
        return self

    def build(self):
        assert self.name is not None, "name must be set"
        G.modloader(self.modname, "special:datagen:configure")(self.__generate_data_gen)
        G.modloader(self.modname, "stage:block:load")(self.__generate_factories)

    def __generate_data_gen(self):
        name = ":".join(self.name.split(":")[1:])
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name + "_inventory", parent="minecraft:block/wall_inventory").set_texture_variable(
            "wall", self.texture)
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name + "_post", parent="minecraft:block/template_wall_post").set_texture_variable(
            "wall", self.texture)
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name + "_side", parent="minecraft:block/template_wall_side").set_texture_variable(
            "wall", self.texture)
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name + "_side_tall", parent="minecraft:block/template_wall_side_tall").set_texture_variable(
            "wall", self.texture)
        side = "{}:block/{}_side".format(self.modname, name)
        tall = "{}:block/{}_side_tall".format(self.modname, name)
        mcpython.datagen.BlockModelGenerator.MultiPartBlockStateGenerator(
            self.config, name).add_state("up=true", "{}:block/{}_post".format(self.modname, name)).add_state(
            "north=low", side).add_state("east=low", ModelRepresentation(side, r_y=90)).add_state(
            "south=low", ModelRepresentation(side, r_y=180)).add_state("west=low", ModelRepresentation(
                side, r_y=270)).add_state("north=tall", tall).add_state(
            "east=tall", ModelRepresentation(tall, r_y=90)).add_state("south=tall", ModelRepresentation(
                tall, r_y=180)).add_state("west=tall", ModelRepresentation(tall, r_y=270))

    def __generate_factories(self):
        factory = mcpython.factory.BlockFactory.BlockFactory().setName(self.name)
        factory.baseclass = [mcpython.block.BlockWall.IWall]
        if self.on_create_callback is not None: self.on_create_callback(self, factory)
        factory.finish()


class CombinedLogFactory:
    """
    CombinedFactory for logs
    """

    GLOBAL_NAME = None

    def __init__(self, front_texture: str, side_texture: str, modname=None, config=None, on_create_callback=None):
        """
        will create an new CombinedWallFactory
        :param texture: the texture for the slab
        :param modname: the modname, if not set globally
        :param config: the config to use
        :param on_create_callback: callback when BlockFactory is active
        """
        if modname is None: modname = self.GLOBAL_NAME
        assert modname is not None, "modname must be set locally or globally"
        if config is None: config = mcpython.datagen.Configuration.DataGeneratorConfig(modname,
                                                                                       G.modloader.mods[modname].path)
        self.config = config
        self.front_texture = front_texture
        self.side_texture = side_texture
        self.modname = modname
        self.name = None
        self.on_create_callback = on_create_callback
        G.modloader(modname, "stage:combined_factory:build")(self.build)

    def setName(self, name: str):
        self.name = name
        return self

    def build(self):
        assert self.name is not None, "name must be set"
        G.modloader(self.modname, "special:datagen:configure")(self.__generate_data_gen)
        G.modloader(self.modname, "stage:block:load")(self.__generate_factories)

    def __generate_data_gen(self):
        name = ":".join(self.name.split(":")[1:])
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name, parent="minecraft:block/cube_column").set_texture_variable(
            "end", self.front_texture).set_texture_variable("side", self.side_texture)
        mcpython.datagen.BlockModelGenerator.BlockModelGenerator(
            self.config, name + "_horizontal", parent="minecraft:block/cube_column_horizontal").set_texture_variable(
            "end", self.front_texture).set_texture_variable("side", self.side_texture)
        hor = "{}:block/{}_horizontal".format(self.modname, name)
        mcpython.datagen.BlockModelGenerator.BlockStateGenerator(
            self.config, name).add_state("axis=x", ModelRepresentation(hor, r_x=90, r_y=90)).add_state(
            "axis=y", "{}:block/{}".format(self.modname, name)).add_state("axis=z", ModelRepresentation(hor, r_x=90))

    def __generate_factories(self):
        factory = mcpython.factory.BlockFactory.BlockFactory().setName(self.name).setLog()
        if self.on_create_callback is not None: self.on_create_callback(self, factory)
        factory.finish()


def set_global_mod_name(modname: typing.Union[str, None]):
    CombinedFullBlockFactory.GLOBAL_NAME = modname
    CombinedSlabFactory.GLOBAL_NAME = modname
    CombinedWallFactory.GLOBAL_NAME = modname
    CombinedLogFactory.GLOBAL_NAME = modname