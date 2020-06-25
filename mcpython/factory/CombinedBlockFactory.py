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


def generate_full_block_slab_wall(config: mcpython.datagen.Configuration.DataGeneratorConfig, name: str, texture: str,
                                  enable=(True, True, True)):
    modname, raw_name = name.split(":")
    if enable[0]:
        CombinedFullBlockFactory(modname, config).setName(name).setTextureVariable("all", texture)
    if enable[1]:
        CombinedSlabFactory(texture, modname, config, full_model="{}:block/{}".format(modname, raw_name)).setName(
            name + "_slab")
    if enable[2]:
        CombinedWallFactory(texture, modname, config).setName(name+"_wall")


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


def set_global_mod_name(modname: typing.Union[str, None]):
    CombinedFullBlockFactory.GLOBAL_NAME = modname
    CombinedSlabFactory.GLOBAL_NAME = modname
    CombinedWallFactory.GLOBAL_NAME = modname
