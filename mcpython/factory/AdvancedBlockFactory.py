"""mcpython - a minecraft clone written in pure python licenced under MIT-licence
authors: uuk, xkcdjerry (inactive)

based on the game of fogleman (https://github.com/fogleman/Minecraft) licenced under MIT-licence
original game "minecraft" by Mojang (www.minecraft.net)
mod loader inspired by "minecraft forge" (https://github.com/MinecraftForge/MinecraftForge)

blocks based on 1.16.1.jar of minecraft"""
import mcpython.factory.BlockFactory
import mcpython.factory.BlockModelFactory
import mcpython.event.Registry
from mcpython import globals as G, logger
import deprecation
# todo: re-write to be based on new data gen system


@deprecation.deprecated("dev4-2", "a1.4.0")
class IAdvancedBlockFactoryMode(mcpython.event.Registry.IRegistryContent):
    TYPE = "minecraft:advanced_block_factory_mode"

    REQUIRED_SETTINGS = None
    OPTIONAL_SETTINGS = []

    @classmethod
    @deprecation.deprecated("dev4-2", "a1.4.0")
    def work(cls, factory_instance, settings: dict):
        raise NotImplementedError()


advanced_block_factory_mode_registry = mcpython.event.Registry.Registry(
    "advanced_block_factory_mode", ["minecraft:advanced_block_factory_mode"], dump_content_in_saves=False,
    injection_function=lambda x: logger.println("[DEPRECATION][WARN] object '{}' was registered to "
                                                "AdvancedBlockFactory-registry which is deprecated".format(x)))


@deprecation.deprecated("dev4-2", "a1.4.0")
@G.registry
class FullCube(IAdvancedBlockFactoryMode):
    NAME = "minecraft:model_full_cube"

    REQUIRED_SETTINGS = [("texture",), ("textures",)]
    OPTIONAL_SETTINGS = []

    @classmethod
    @deprecation.deprecated("dev4-2", "a1.4.0")
    def work(cls, factory_instance, settings: dict):
        if "texture" in settings:
            assert type(settings["texture"]) == str
            mcpython.factory.BlockModelFactory.BlockModelFactory().setName(factory_instance.name).setParent("block/cube_all").\
                setTexture("all", settings["texture"]).finish()
        elif "textures" in settings:
            assert type(settings["textures"]) == dict
            obj = mcpython.factory.BlockModelFactory.BlockModelFactory().setName(factory_instance.name).setParent("minecraft:block/cube")
            obj.textures = settings["textures"]
            obj.finish()
        mcpython.factory.BlockModelFactory.NormalBlockStateFactory().setName(factory_instance.name).addVariant(
            "default", factory_instance.name).finish()


@deprecation.deprecated("dev4-2", "a1.4.0")
@G.registry
class SlabBlock(IAdvancedBlockFactoryMode):
    NAME = "minecraft:model_slab_block"

    REQUIRED_SETTINGS = [("texture",), ("textures",)]
    OPTIONAL_SETTINGS = []

    @classmethod
    @deprecation.deprecated("dev4-2", "a1.4.0")
    def work(cls, factory_instance, settings: dict):
        if "texture" in settings:
            assert type(settings["texture"]) == str
            tex = settings["texture"]
            mcpython.factory.BlockModelFactory.BlockModelFactory().setName(factory_instance.name).setParent("block/slab"). \
                setTexture("top", tex).setTexture("bottom", tex).setTexture("side", tex).finish()
            mcpython.factory.BlockModelFactory.BlockModelFactory().setName(factory_instance.name+"_top").setParent(
                "block/slab_top").setTexture("top", tex).setTexture("bottom", tex).setTexture("side", tex).finish()
            mcpython.factory.BlockModelFactory.BlockModelFactory().setName(factory_instance.name).setParent(
                "block/cube_all_full").setTexture("all", tex).finish()
        elif "textures" in settings:
            assert type(settings["textures"]) == dict
            obj = mcpython.factory.BlockModelFactory.BlockModelFactory().setName(factory_instance.name).setParent("minecraft:block/cube")
            obj.textures = settings["textures"]
            obj.finish()
        mcpython.factory.BlockModelFactory.NormalBlockStateFactory().setName(factory_instance.name).addVariant(
            "type=bottom", factory_instance.name).addVariant("type=top", factory_instance.name+"_top").addVariant(
            "type=double", factory_instance.name+"_full").finish()

        factory_instance.block_factory.setSlab()


@deprecation.deprecated("dev4-2", "a1.4.0")
class SimpleBlockFactoryHelper(mcpython.factory.BlockFactory.BlockFactory):
    """
    representation of an BlockFactory linked to an AdvancedBlockFactory for returning back to the AdvancedBlockFactory
    """

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def __init__(self, master):
        super().__init__()
        self.master = master

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def getMaster(self):
        return self.master

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def finish(self, register=True):
        self.master.finish()

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def default_finish(self):
        super().finish()


@deprecation.deprecated("dev4-2", "a1.4.0")
class AdvancedBlockFactory:
    """
    factory class for blocks without the data FILES located. Generating when needed
    """

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def __init__(self):
        self.name = None
        self.block_factory = SimpleBlockFactoryHelper(self)
        self.mode = FullCube
        self.settings = None

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def setName(self, name: str):
        self.name = name
        self.block_factory.setName(name)
        return self

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def getSimpleFactory(self):
        return self.block_factory

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def setMode(self, name: str):
        assert self.settings is None
        self.mode = advanced_block_factory_mode_registry.registered_object_map[name]
        return self

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def setModelConfig(self, key, value):
        assert self.mode is not None
        assert any([key in l for l in self.mode.REQUIRED_SETTINGS]) or key in self.mode.OPTIONAL_SETTINGS
        if self.settings is None: self.settings = {}
        self.settings[key] = value
        return self

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def finish(self):
        assert self.mode is not None
        assert self.settings is not None or len(self.mode.REQUIRED_SETTINGS) == 0
        k = tuple(self.settings.keys())
        assert k in self.mode.REQUIRED_SETTINGS, "configuration MUST be allowed!"
        assert self.name is not None
        modname, blockname = tuple(self.name.split(":"))
        if modname not in G.modloader.mods: modname = "minecraft"
        G.modloader.mods[modname].eventbus.subscribe("stage:block:load", self.finish_up,
                                                     info="loading block {}".format(blockname))

    @deprecation.deprecated("dev4-2", "a1.4.0")
    def finish_up(self):
        self.mode.work(self, self.settings)
        self.block_factory.finish_up()

